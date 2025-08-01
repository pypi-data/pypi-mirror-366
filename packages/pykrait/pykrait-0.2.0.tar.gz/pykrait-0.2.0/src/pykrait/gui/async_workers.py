from PySide6.QtCore import QObject, Signal, Slot
import tifffile
import warnings
import os
import traceback
import numpy as np

from pykrait.io.io import load_timelapse_lazy
from pykrait.preprocessing.segmentation import timelapse_projection, create_cellpose_segmentation
from pykrait.preprocessing.timeseries_extraction import extract_mean_intensities
from pykrait.trace_analysis.filtering import detrend_with_sinc_filter
from pykrait.trace_analysis.peak_analysis import find_peaks
from pykrait.trace_analysis.oscillations import find_oscillating_rois
from pykrait.pipeline.pipeline import AnalysisParameters, AnalysisOutput

class ExtractIntensitiesWorker(QObject):
    progress_changed = Signal(int, str)    # progress percent, status message
    finished = Signal(dict)                # analysis results
    error = Signal(str)                    # error message

    def __init__(self, analysis_params:AnalysisParameters, output_params:AnalysisOutput, mode:str):
        super().__init__()
        self.analysis_parameters = analysis_params
        self.analysis_output = output_params
        self.mode = mode

    @Slot()
    def run(self):
        try:
            
            self.analysis_output.filename = self.analysis_output.filepath.split("/")[-1]
            print(f"Running analysis on {self.analysis_output.filename}")
            # Create analysis folder in the parent directory of the video file
            parent_dir = os.path.dirname(self.analysis_output.filepath)
            filename_wo_ext = os.path.splitext(self.analysis_output.filename)[0]
            analysis_folder = os.path.join(parent_dir, f"Analysis_{filename_wo_ext}")
            os.makedirs(analysis_folder, exist_ok=True)
            self.analysis_output.analysis_folder = analysis_folder

            self.progress_changed.emit(5, "Loading timelapse...")

            timelapse_data, frame_interval, self.analysis_output.pixel_interval_y, self.analysis_output.pixel_interval_x = load_timelapse_lazy(file_path = self.analysis_output.filepath)

            if frame_interval is None and self.analysis_parameters.frame_interval is None:
                warnings.warn("No frame interval provided in the analysis parameters, and no frame interval could be inferred from the metadata. Defaulting to 1 second.")
                self.analysis_output.frame_interval = 1  # Default to 1 second if not provided
            elif self.analysis_parameters.frame_interval is None and frame_interval is not None:
                self.analysis_output.frame_interval = frame_interval
            elif frame_interval is not None and self.analysis_parameters.frame_interval != frame_interval:
                warnings.warn(f"Provided frame_interval ({self.analysis_parameters.frame_interval}) does not match inferred frame_interval ({frame_interval}) from metadata. Using provided value.")

            if self.mode == "cellpose":
                # perform the tproj
                self.progress_changed.emit(10, "Performing T Projection...")
                tproj = timelapse_projection(timelapse_data, method=self.analysis_parameters.tproj_type, normalize=self.analysis_parameters.CLAHE_normalize, verbose=True)
                tproj_path = os.path.join(analysis_folder, f"{filename_wo_ext}_tproj.ome.tif")
                self.analysis_output.tproj_path = tproj_path
                tifffile.imwrite(tproj_path, tproj.astype(np.uint16), metadata={'axes': 'CYX'}, compression="zlib")
                self.analysis_output.zproj_path = os.path.join(analysis_folder, f"{filename_wo_ext}_zproj.ome.tif")

                # create cellpose segmentation
                self.progress_changed.emit(30, "Performing Cellpose Segmentation...")    
                masks = create_cellpose_segmentation(tproj, cellpose_model_path=self.analysis_parameters.cellpose_model_path)
                mask_path = os.path.join(analysis_folder, f"{filename_wo_ext}_cp_masks.ome.tif")
                self.analysis_output.mask_path = mask_path
                tifffile.imwrite(mask_path, masks.astype(np.uint16), metadata={'axes': 'YX'}, compression="zlib")
                
            elif self.mode == "label_image":
                self.progress_changed.emit(20, "Loading label image...")
                masks = tifffile.imread(self.analysis_output.masks_path)
                tproj = None  # Not needed in this mode

            else:
                raise ValueError("Unknown mode.")

            # extracts the mean intensities of the masks
            self.progress_changed.emit(60, "Extracting intensities...") 
            mean_intensities = extract_mean_intensities(timelapse_data, masks)
            self.analysis_output.number_of_frames, self.analysis_output.number_of_cells = mean_intensities.shape

            # All done
            self.progress_changed.emit(100, "Done.")
            
            results = {
                'frames': timelapse_data,
                'analysis_output': self.analysis_output,
                'analysis_parameters': self.analysis_parameters,
                'masks': masks,
                'mean_intensities': mean_intensities
            }
            self.finished.emit(results)

        except Exception as e:
            tb = traceback.format_exc()
            print(f"Error during analysis: {e}\n{tb}")
            self.error.emit(str(e))

class DetrendWorker(QObject):
    finished = Signal(np.ndarray)
    error = Signal(Exception)

    def __init__(self, intensities, sinc_window, frame_interval):
        super().__init__()
        self.intensities = intensities
        self.sinc_window = sinc_window
        self.frame_interval = frame_interval

    def run(self):
        try:
            # Call your actual function here
            detrended = detrend_with_sinc_filter(signals=self.intensities, 
                                                 cutoff_period=self.sinc_window,
                                                 sampling_interval=self.frame_interval)
            self.finished.emit(detrended)
        except Exception as e:
            self.error.emit(e)


class PeakDetectionWorker(QObject):
    finished = Signal(np.ndarray)
    error = Signal(Exception)

    def __init__(self, detrended_traces, min_width, max_width, prominence, min_height):
        super().__init__()
        self.traces = detrended_traces
        self.min_width = min_width
        self.max_width = max_width
        self.prominence = prominence
        self.min_height = min_height

    def run(self):
        try:
            peaks = find_peaks(
                peak_min_width=self.min_width,
                peak_max_width=self.max_width,
                peak_prominence=self.prominence,
                peak_min_height=self.min_height,
                detrended_timeseries=self.traces
            )
            self.finished.emit(peaks)
        except Exception as e:
            self.error.emit(e)

class PeriodicCellWorker(QObject):
    finished = Signal(float, int, int, float, int, int)
    error = Signal(Exception)

    def __init__(self, peaks: np.ndarray, frame_interval: float, std_t: float = 0.01, cov_t: float = 0.01):
        super().__init__()
        self.peaks = peaks
        self.frame_interval = frame_interval
        self.std_t = std_t
        self.cov_t = cov_t

    def run(self):
        try:
            filtered_peak_series = self.peaks[:, np.sum(self.peaks, axis=0) >= 4]
            result = find_oscillating_rois(
                filtered_peak_series,
                std_threshold=self.std_t,
                cov_threshold=self.cov_t,
                frame_interval=self.frame_interval,
            )
            self.finished.emit(*result)
        except Exception as e:
            self.error.emit(e)

