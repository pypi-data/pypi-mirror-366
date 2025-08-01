import os
import numpy as np
import dask.array as da
from matplotlib import cm

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QLabel,
    QFormLayout, QPushButton, QSplitter, QSlider, QDoubleSpinBox, QGroupBox,
    QCheckBox
)
from PySide6.QtCore import Qt, QPointF, Signal, QThread
from PySide6.QtGui import QImage, QPixmap, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsPolygonItem

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from skimage.measure import find_contours

from pykrait.io.io import get_pykrait_version
from pykrait.pipeline.pipeline import AnalysisParameters, AnalysisOutput
from pykrait.gui.async_workers import DetrendWorker, PeakDetectionWorker, PeriodicCellWorker
from pykrait.trace_analysis.peak_analysis import calculate_normalized_peaks

def get_pixel_contour_from_label_img(label_img:np.ndarray, orig_shape:tuple, target_shape:tuple) -> list:
    """
    Generates pixel contours from a labeled image, scaled to a target shape.

    :param label_img: a label image where each pixel is labeled with an integer representing the ROI it belongs to
    :type label_img: np.ndarray
    :param orig_shape: original shape of the image (height, width)
    :type orig_shape: tuple
    :param target_shape: target shape to which the contours should be scaled (height, width)
    :type target_shape: tuple
    :return: returns a list of polygons representing the scaled contours of each ROI
    :rtype: list
    """ 
    roi_polygons = []
    orig_height, orig_width = orig_shape
    target_height, target_width = target_shape
    scale_y = target_height / orig_height
    scale_x = target_width / orig_width
    for index in range(1, label_img.max() + 1):  # skip background (0)
        contours = find_contours(label_img == index, 0.5)
        if contours:
            contour = contours[0]
            y, x = contour.T
            y, x = y * scale_y, x * scale_x # rescales coordinates to target shape
            polygon = list(zip(x, y))
            roi_polygons.append(polygon)
    return roi_polygons

class ImageDisplay(QGraphicsView):
    roiSelected = Signal(int)

    def __init__(self, parent=None, target_shape=(512, 512)):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.image_item = QGraphicsPixmapItem()
        self.scene.addItem(self.image_item)
        self.roi_items = []
        self.rois = []
        self.target_shape = target_shape  #target shape for downsampling
        self.selected_roi = None # to track the active ROI
        self.last_sinc_window = None  # to track the last used sinc window for detrending
        self.intensity_clip_min = None
        self.intensity_clip_max = None

    def set_rois(self, rois):
        # Clear old ROIs
        for item in self.roi_items:
            self.scene.removeItem(item)
        self.roi_items.clear()
        self.rois = rois

        for i, poly_pts in enumerate(rois):
            polygon = QPolygonF([QPointF(x, y) for x, y in poly_pts])
            pen = QPen(Qt.white)             # White color
            pen.setWidth(1)                  # Line width
            pen.setStyle(Qt.DashLine)        # Dashed line
            roi_item = QGraphicsPolygonItem(polygon)
            roi_item.setPen(pen)
            roi_item.setBrush(Qt.NoBrush)    # No fill
            roi_item.setZValue(1)
            roi_item.setData(0, i)
            self.scene.addItem(roi_item)
            self.roi_items.append(roi_item)
        self.highlight_selected_roi()

    def highlight_selected_roi(self):
        for i, roi_item in enumerate(self.roi_items):
            if i == self.selected_roi:
                pen = QPen(Qt.red)
                pen.setWidth(3)
                pen.setStyle(Qt.SolidLine)
                roi_item.setZValue(100)      # Highest level for selected
            else:
                pen = QPen(Qt.white)
                pen.setWidth(1)
                pen.setStyle(Qt.DashLine)
                roi_item.setZValue(1)        # Normal level for unselected
            roi_item.setPen(pen)
            roi_item.setBrush(Qt.NoBrush)

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        for idx, roi_item in enumerate(self.roi_items):
            if roi_item.contains(scene_pos):
                self.selected_roi = idx
                self.highlight_selected_roi()
                self.roiSelected.emit(idx)  # <---- emit the signal
                break
        else:
            self.selected_roi = None
            self.highlight_selected_roi()
        super().mousePressEvent(event)

    def display_dask_frame(self, frame:da.Array, cmap='magma'):
        """
        displays a single frame from a dask array in the QGraphicsView.
        Uses coarsening to downsample the frame, and normalizes the brightness consistently.

        :param frame: dask array representing a single frame of the timelapse
        :type frame: da.Array
        :param cmap: colormap to display in, defaults to 'magma'
        :type cmap: str, optional
        :raises ValueError: raises ValueError if the input frame is not a 2D array
        :raises ValueError: raises ValueError if the original frame is too small for the target
        """        
        if frame.ndim != 2:
            raise ValueError("Input frame must be a 2D array")
        h, w = frame.shape

        # Compute coarsening factors
        fh, fw = h // self.target_shape[0], w // self.target_shape[1]
        if fh < 1 or fw < 1:
            raise ValueError(f"Original frame too small for target {self.target_shape}")

        # Downsample using mean pooling
        frame_ds = da.coarsen(np.mean, frame, {0: fh, 1: fw}, trim_excess=True)
        img = frame_ds.compute()

        # Normalize the image for optimized display
        if self.intensity_clip_min is None:
            self.intensity_clip_min = np.percentile(img, 1) # 1st percentile for better contrast
        if self.intensity_clip_max is None:
            self.intensity_clip_max = np.percentile(img, 99)
        # Avoid divide-by-zero
        if self.intensity_clip_max - self.intensity_clip_min < 1e-6:
            norm = np.zeros_like(img, dtype=float)
        else:
            norm = np.clip((img - self.intensity_clip_min) / (self.intensity_clip_max - self.intensity_clip_min), 0, 1)

        # Apply colormap
        img_rgb = (cm.get_cmap(cmap)(norm)[..., :3] * 255).astype(np.uint8)


        # Convert to QImage and display
        h_ds, w_ds, _ = img_rgb.shape
        qimg = QImage(img_rgb.data, w_ds, h_ds, 3 * w_ds, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        self.image_item.setPixmap(pix)
        self.fitInView(self.image_item, Qt.KeepAspectRatio)


class MainWindow(QMainWindow):
    def __init__(self, frames:da.Array, mask:np.ndarray, mean_intensities:np.ndarray, analysis_output:AnalysisOutput, analysis_params:AnalysisParameters):
        super().__init__()
        self.frames = frames
        self.mask = mask
        self.rois = get_pixel_contour_from_label_img(label_img=self.mask, orig_shape=self.mask.shape, target_shape=(512, 512))
        self.intensities = mean_intensities
        self.setWindowTitle("Calcium Imaging Analysis")
        self.analysis_output = analysis_output
        self.analysis_params = analysis_params

        self.selected_roi = 0  # Default to first ROI
        self.current_frame = 0
        self.show_detrended:bool = False
        self.detrended_intensities = None
        self.peaks = None

        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # -------- LEFT PANEL --------
        left_panel = QVBoxLayout()
        
        # Image display
        self.image_display = ImageDisplay()
        self.image_display.setMinimumSize(400, 400)
        left_panel.addWidget(self.image_display)

        # Video slider
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(self.frames.shape[0]-1)  # Use -1 for index
        left_panel.addWidget(self.frame_slider)

        # Intensity plot
        self.fig = Figure(figsize=(4, 2))
        self.canvas = FigureCanvas(self.fig)
        left_panel.addWidget(self.canvas)
        self.ax = self.fig.add_subplot(111)

        # -------- RIGHT PANEL --------
        right_panel = QVBoxLayout()

        # --- Trace Detrending Group ---
        trace_group = QGroupBox("Trace Detrending")
        trace_layout = QFormLayout()
        # Sinc filter window
        self.sinc_filter_spin = QDoubleSpinBox()
        self.sinc_filter_spin.setDecimals(2)
        sinc_max = self.frames.shape[0] * self.analysis_output.frame_interval
        self.sinc_filter_spin.setMinimum(1)
        self.sinc_filter_spin.setMaximum(sinc_max)
        self.sinc_filter_spin.setValue(int(self.frames.shape[0] * self.analysis_output.frame_interval / 2))  # Default to half the total time
        trace_layout.addRow("Sinc Filter Window [s]:", self.sinc_filter_spin)
        # Frame Interval and Video Duration Display
        self.frame_interval_value = QLabel(f"{self.analysis_output.frame_interval:.2f}")
        trace_layout.addRow("Frame Interval [s]:", self.frame_interval_value)
        self.video_duration_value = QLabel(f"{self.analysis_output.frame_interval*self.intensities.shape[0]:.2f}")
        trace_layout.addRow("Video Duration [s]:", self.video_duration_value)

        # Trace display buttons on one row
        trace_btn_layout = QHBoxLayout()
        self.show_detrended_btn = QPushButton("Show Detrended Traces")
        self.show_raw_btn = QPushButton("Show Raw Traces")
        trace_btn_layout.addWidget(self.show_detrended_btn)
        trace_btn_layout.addWidget(self.show_raw_btn)
        trace_layout.addRow(trace_btn_layout)
        trace_group.setLayout(trace_layout)
        right_panel.addWidget(trace_group)

        # --- Peak Identification Group ---
        peak_group = QGroupBox("Peak Identification")
        peak_layout = QFormLayout()
        self.peak_min_width_spin = QDoubleSpinBox()
        self.peak_min_width_spin.setDecimals(2)
        self.peak_min_width_spin.setMinimum(1)
        self.peak_min_width_spin.setMaximum(1000)
        self.peak_min_width_spin.setValue(1.0)
        peak_layout.addRow("Peak Min Width [s]:", self.peak_min_width_spin)

        self.peak_max_width_spin = QDoubleSpinBox()
        self.peak_max_width_spin.setDecimals(2)
        self.peak_max_width_spin.setMinimum(0)
        self.peak_max_width_spin.setMaximum(1000)
        self.peak_max_width_spin.setValue(80.0)
        peak_layout.addRow("Peak Max Width [s]:", self.peak_max_width_spin)

        self.peak_min_height_spin = QDoubleSpinBox()
        self.peak_min_height_spin.setDecimals(0)
        self.peak_min_height_spin.setMinimum(0)
        self.peak_min_height_spin.setMaximum(65535)
        self.peak_min_height_spin.setValue(800)
        peak_layout.addRow("Peak Min Height [au]:", self.peak_min_height_spin)

        self.peak_prominence_spin = QDoubleSpinBox()
        self.peak_prominence_spin.setDecimals(0)
        self.peak_prominence_spin.setMinimum(0)
        self.peak_prominence_spin.setMaximum(65535)
        self.peak_prominence_spin.setValue(1500)
        peak_layout.addRow("Peak Prominence [au]:", self.peak_prominence_spin)

        self.find_peaks_btn = QPushButton("Find Peaks")
        peak_layout.addRow(self.find_peaks_btn)
        self.norm_peak_label = QLabel("")
        self.fourpeak_label = QLabel("")
        self.fourpeak_frequency_label = QLabel("")
        peak_layout.addRow("normalized peaks:", self.norm_peak_label)
        peak_layout.addRow("cells w/ >= 4 peaks:", self.fourpeak_label)
        peak_layout.addRow("% of cells w/ >= 4 peaks:", self.fourpeak_frequency_label)

        peak_group.setLayout(peak_layout)
        right_panel.addWidget(peak_group)

        # Periodicity
        periodicity_group = QGroupBox("Periodic Cells")
        periodicity_layout = QFormLayout()
        self.periodicity_cutoff_std_SpinBox = QDoubleSpinBox()
        self.periodicity_cutoff_std_SpinBox.setDecimals(2)
        self.periodicity_cutoff_std_SpinBox.setMinimum(0)
        self.periodicity_cutoff_std_SpinBox.setMaximum(1000)
        self.periodicity_cutoff_std_SpinBox.setValue(15.0)
        periodicity_layout.addRow("Peak Periodicity Threshold STD [s]:", self.periodicity_cutoff_std_SpinBox)
        self.periodicity_cutoff_cov_SpinBox = QDoubleSpinBox()
        self.periodicity_cutoff_cov_SpinBox.setDecimals(2)
        self.periodicity_cutoff_cov_SpinBox.setMinimum(0)
        self.periodicity_cutoff_cov_SpinBox.setMaximum(1)
        self.periodicity_cutoff_cov_SpinBox.setValue(0.2)
        periodicity_layout.addRow("Peak Periodicity Threshold CoV:", self.periodicity_cutoff_cov_SpinBox)
        self.periodicity_button = QPushButton("Find Periodic Cells")
        periodicity_layout.addRow(self.periodicity_button)

        self.std_periodic_per_active_label = QLabel("")
        self.cov_periodic_per_active_label = QLabel("")
        periodicity_layout.addRow("Cells < STD Threshold per Active Cells:", self.std_periodic_per_active_label)
        periodicity_layout.addRow("Cells < CoV Threshold per Active Cells:", self.cov_periodic_per_active_label)
        periodicity_group.setLayout(periodicity_layout)
        right_panel.addWidget(periodicity_group)
        right_panel.addStretch()

        # Saving
        save_group = QGroupBox("Saving")
        save_layout = QVBoxLayout()
        save_row_layout = QHBoxLayout()

        self.overwrite_checkbox = QCheckBox("Overwrite")
        self.overwrite_checkbox.setChecked(True)
        self.save_btn = QPushButton("Save Analysis")
        self.save_btn.clicked.connect(self._save_analysis_results)

        save_row_layout.addWidget(self.save_btn)
        save_row_layout.addWidget(self.overwrite_checkbox)

        save_layout.addLayout(save_row_layout) 
        save_group.setLayout(save_layout)      
        right_panel.addWidget(save_group)

        # --- Splitter ---
        splitter = QSplitter(Qt.Horizontal)
        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel)
        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel)
        splitter.addWidget(left_panel_widget)
        splitter.addWidget(right_panel_widget)
        splitter.setSizes([700, 250])
        main_layout.addWidget(splitter)

        # set data
        self.image_display.set_rois(self.rois)
        self.image_display.display_dask_frame(self.frames[0, 0, :, :]) # TCYX format
        self.update_intensity_trace()

        # Connecting buttons and signals
        self.frame_slider.valueChanged.connect(self.on_slider_moved)
        self.show_raw_btn.clicked.connect(self.show_raw_traces)
        self.show_detrended_btn.clicked.connect(self.show_detrended_traces)
        self.image_display.roiSelected.connect(self.roi_selected)
        self.find_peaks_btn.clicked.connect(self.find_peaks)
        self.periodicity_button.clicked.connect(self._start_periodicity_worker)

    def on_slider_moved(self, idx):
        self.current_frame = idx
        self.image_display.display_dask_frame(self.frames[self.current_frame, 0, :, :])
        self.update_intensity_trace()

    def roi_selected(self, idx):
        self.selected_roi = idx
        self.update_intensity_trace()

    def update_intensity_trace(self):
        self.ax.clear()
        color_raw = "#1E2B33"
        color_detrended = "#4C0308"

        if self.show_detrended:
            try:
                self.ax.plot(
                    self.detrended_intensities[:, self.selected_roi],
                    color=color_detrended,
                    label=f"ROI {self.selected_roi}"
                )
                self.ax.set_ylabel("Detrended Intensity")
            except Exception as e:
                print(f"Error plotting detrended intensities: {e}")
        else:
            self.ax.plot(
                self.intensities[:, self.selected_roi],
                color=color_raw,
                label=f"ROI {self.selected_roi}"
            )
            self.ax.set_ylabel("Raw Intensity")
        
        if hasattr(self, 'peaks') and self.peaks is not None:
            peak_indices = np.where(self.peaks[:, self.selected_roi] == 1)[0]
            self.ax.plot(peak_indices,
                        (self.detrended_intensities if self.show_detrended else self.intensities)[peak_indices, self.selected_roi],
                        'bx', markersize=4)


        self.ax.axvline(self.current_frame, color='k', linestyle='--')
        self.ax.set_xlabel('Frame')
        self.ax.legend()
        self.canvas.draw()

    def show_raw_traces(self):
        self.show_detrended = False
        self.update_intensity_trace()

    def show_detrended_traces(self):
        sinc_value = self.sinc_filter_spin.value()
        # If needed, recompute
        needs_recompute = (
            self.detrended_intensities is None
            or self.last_sinc_window != sinc_value
        )
        if needs_recompute:
            # Optionally show a progress bar or message here
            # start computing
            self._start_detrend_worker(sinc_value)
        else:
            self.show_detrended = True
            self.update_intensity_trace()

    def find_peaks(self):
        if self.detrended_intensities is None:
            QMessageBox.warning(self, "Missing Data", "Detrended traces are required. Please detrend first.")
            return

        frame_interval = self.analysis_output.frame_interval

        # Convert time-based spinboxes to frame units
        min_width = int(self.peak_min_width_spin.value() / frame_interval)
        max_width = int(self.peak_max_width_spin.value() / frame_interval)
        prominence = self.peak_prominence_spin.value()
        min_height = self.peak_min_height_spin.value()

        self.find_peaks_btn.setEnabled(False)  # Prevent repeat clicks

        # Launch async worker
        self.peak_thread = QThread()
        self.peak_worker = PeakDetectionWorker(
            detrended_traces=self.detrended_intensities,
            min_width=min_width,
            max_width=max_width,
            prominence=prominence,
            min_height=min_height
        )
        self.peak_worker.moveToThread(self.peak_thread)
        self.peak_thread.started.connect(self.peak_worker.run)
        self.peak_worker.finished.connect(self._peaks_detected)
        self.peak_worker.error.connect(self._peak_error)
        self.peak_worker.finished.connect(self.peak_thread.quit)
        self.peak_worker.finished.connect(self.peak_worker.deleteLater)
        self.peak_thread.finished.connect(self.peak_thread.deleteLater)
        self.peak_thread.start()



    def _start_detrend_worker(self, sinc_value):
        self.detrend_thread = QThread()
        self.detrend_worker = DetrendWorker(self.intensities, sinc_value, self.analysis_output.frame_interval)
        self.detrend_worker.moveToThread(self.detrend_thread)
        self.detrend_thread.started.connect(self.detrend_worker.run)
        self.detrend_worker.finished.connect(self._detrend_done)
        self.detrend_worker.error.connect(self._detrend_error)
        self.detrend_worker.finished.connect(self.detrend_thread.quit)
        self.detrend_worker.finished.connect(self.detrend_worker.deleteLater)
        self.detrend_thread.finished.connect(self.detrend_thread.deleteLater)
        self.detrend_thread.start()

    def _detrend_done(self, detrended):
        self.detrended_intensities = detrended
        self.analysis_params.sinc_filter_window = self.sinc_filter_spin.value()
        self.last_sinc_window = self.sinc_filter_spin.value()
        # Optionally hide progress bar or message here
        self.show_detrended = True
        self.update_intensity_trace()

    def _detrend_error(self, error):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", f"Detrending failed: {error}")

    def _peaks_detected(self, peaks):
        self.peaks = peaks
        self.find_peaks_btn.setEnabled(True)
        self.analysis_output.normalized_peaks = calculate_normalized_peaks(peaks, self.analysis_output.frame_interval)
        self.analysis_output.cells_four_peaks = np.sum(np.sum(self.peaks, axis=0) >= 4)
        percentage_four_peaks = (self.analysis_output.cells_four_peaks / self.peaks.shape[0]) * 100

        # display the peak stats
        self.norm_peak_label.setText(f"{self.analysis_output.normalized_peaks:.2f}")
        self.fourpeak_label.setText(f"{self.analysis_output.cells_four_peaks}")
        self.fourpeak_frequency_label.setText(f"{percentage_four_peaks:.0f}%")

        # update the intensity trace to show peaks
        self.update_intensity_trace()

    def _peak_error(self, error):
        QMessageBox.critical(self, "Error", f"Peak detection failed: {error}")
        self.find_peaks_btn.setEnabled(True)

    def _start_periodicity_worker(self):
        if self.peaks is None:
            QMessageBox.warning(self, "Missing Data", "Run peak detection before computing periodicity.")
            return

        std_t = self.periodicity_cutoff_std_SpinBox.value()
        cov_t = self.periodicity_cutoff_cov_SpinBox.value()
        frame_interval = self.analysis_output.frame_interval

        self.periodicity_thread = QThread()
        self.periodicity_worker = PeriodicCellWorker(
            peaks=self.peaks,
            frame_interval=frame_interval,
            std_t=std_t,
            cov_t=cov_t,
        )
        self.periodicity_worker.moveToThread(self.periodicity_thread)
        self.periodicity_thread.started.connect(self.periodicity_worker.run)
        self.periodicity_worker.finished.connect(self._periodicity_done)
        self.periodicity_worker.error.connect(self._periodicity_error)
        self.periodicity_worker.finished.connect(self.periodicity_thread.quit)
        self.periodicity_worker.finished.connect(self.periodicity_worker.deleteLater)
        self.periodicity_thread.finished.connect(self.periodicity_thread.deleteLater)
        self.periodicity_thread.start()

    def _periodicity_done(self, std_t, exp_std, rand_std, cov_t, exp_cov, rand_cov):
        self.analysis_output.std_threshold = std_t
        self.analysis_output.experiment_below_std = exp_std
        self.analysis_output.random_below_std = rand_std
        self.analysis_output.cov_threshold = cov_t
        self.analysis_output.experiment_below_cov = exp_cov
        self.analysis_output.random_below_cov = rand_cov
        
        if self.analysis_output.cells_four_peaks == 0:
            self.std_periodic_per_active_label.setText("N/A")
            self.cov_periodic_per_active_label.setText("N/A")
        else:
            perc_std = (exp_std / self.analysis_output.cells_four_peaks) * 100
            perc_cov = (exp_cov / self.analysis_output.cells_four_peaks) * 100
            self.std_periodic_per_active_label.setText(f"{perc_std:.1f}%")
            self.cov_periodic_per_active_label.setText(f"{perc_cov:.1f}%")

    def _periodicity_error(self, error):
        QMessageBox.critical(self, "Error", f"Periodic ROI analysis failed: {error}")

    def _save_analysis_results(self):
        if self.analysis_output is None or self.analysis_params is None:
            QMessageBox.warning(self, "Save Failed", "No analysis data to save.")
            return

        try:
            # Derive save paths
            self.analysis_output.filename = os.path.basename(self.analysis_output.filepath)
            filename_wo_ext = os.path.splitext(self.analysis_output.filename)[0]
            parent_dir = os.path.dirname(self.analysis_output.filepath)
            analysis_folder = os.path.join(parent_dir, f"Analysis_{filename_wo_ext}")

            output_file = os.path.join(analysis_folder, f"{filename_wo_ext}_analysis_output.csv")
            param_file = os.path.join(analysis_folder, f"{filename_wo_ext}_analysis_parameters.csv")

            # Handle overwrite option
            if not self.overwrite_checkbox.isChecked():
                for f in [output_file, param_file]:
                    if os.path.exists(f):
                        QMessageBox.warning(self, "File Exists", "Analysis Output already exists. Uncheck 'Overwrite' to prevent overwrite.")
                        return

            # Save to CSV
            self.analysis_output.pykrait_version = get_pykrait_version()
            self.analysis_output.timestamp = np.datetime64('now')
            self.analysis_output.to_pandas().to_csv(output_file, index=False)
            self.analysis_params.to_pandas().to_csv(param_file, index=False)
            print(f"Analysis results saved to {output_file} and {param_file}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")

