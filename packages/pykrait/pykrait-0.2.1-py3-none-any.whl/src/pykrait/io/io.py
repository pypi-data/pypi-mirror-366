import os
import dask.array as da
import warnings
import re
from importlib.metadata import version, PackageNotFoundError

from bioio import BioImage
import bioio_tifffile

ALLOWED_IMAGE_EXTENSIONS =[".czi", ".tif", ".tiff"]

def load_timelapse_lazy(
    file_path: str,
) -> list[da.Array, float, float, float]:
    """Load a timelapse image file lazily using AICSImageIO, returning a Dask array of the image data along with the frame interval and pixel sizes.

    Currently supports CZI and TIF/TIFF files. The image data is returned as a Dask array with shape (T, C, Y, X) where T is time, C is channels, Y is height, and X is width. The Z dimension is dropped if it has only one slice.

    :param file_path: input file path to the timelapse image file
    :type file_path: str
    :raises TypeError: if filepath is not a string
    :raises FileNotFoundError: if the file does not exist
    :raises ValueError: if the extension is not supported
    :raises ValueError: if the image does not have the expected 5D shape (TCZYX)
    :raises ValueError: if the image has more than one Z slice and Z cannot be automatically dropped
    :return: returns a list of a Dask array containing the image data, the frame interval in seconds, and pixel sizes in micrometers (Y, X)
    :rtype: list[da.Array, float, float, float]
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    ext = os.path.splitext(file_path)[-1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(f"Image to load has the unsupported file format '{ext}'. Supported file formats are: {ALLOWED_IMAGE_EXTENSIONS}")

    # Load with BioImage using Dask
    if ext == ".czi":
        print("Using bioio_czi with aicspylibczi as backend to read")
        img = BioImage(file_path, reconstruct_mosaic=False, use_aicspylibczi=True)
    elif ext in [".tif", ".tiff"]:
        print("Using bioio_tifffile.Reader to read")
        img = BioImage(file_path, reconstruct_mosaic=False, reader=bioio_tifffile.Reader)
    # extract the relevant metadata
    pixel_sizes = img.physical_pixel_sizes  # Units are in micrometers (µm)
    y_um = round(pixel_sizes.Y, 2) if pixel_sizes else None
    x_um = round(pixel_sizes.X, 2) if pixel_sizes else None

    frame_interval = None

    # accessing frame interval from tif/tiff meadata
    if ext == ".tiff" or ext == ".tif":
        try:
                match = re.search(r"finterval=([0-9.]+)", img.metadata)
                raw_finterval = float(match.group(1))
                frame_interval = round(raw_finterval, 2) # Output: 1.26
        except Exception as e:
            warnings.warn(
                f"Failed to extract frame interval from metadata: {type(e).__name__}: {e}", 
                UserWarning
            )
    elif ext == ".czi":
        try:
            frame_interval = img.time_interval.total_seconds()
        except Exception as e:
            warnings.warn(
                f"Failed to extract frame interval from metadata: {type(e).__name__}: {e}", 
                UserWarning
            )
    dask_img = img.dask_data  # TCZYX

    if dask_img.ndim != 5:
        raise ValueError(f"Expected 5D image (TCZYX), but got shape {dask_img.shape}")

    T, C, Z, Y, X = dask_img.shape

    if Z == 1:
        dask_img = dask_img[:, :, 0, :, :]  # shape: (T, C, Z, Y, X)
    else:
        raise ValueError(f"Cannot drop Z dimension automatically: Z={Z}. Consider handling it explicitly.")

    print(f"Returning lazy array of shape {dask_img.shape} (T, C, Y, X)")
    return dask_img, frame_interval, y_um, x_um

def get_files_from_folder(
    folder: str,
    extension: str = ".czi",
) -> list[str]:
    """returns all files from a folder with specified extensions.

    :param folder: path to the folder
    :type folder: str
    :param extensions: str of file extension (default is ".czi")
    :type extensions: str
    :return: list of file paths with the specified extensions
    :rtype: list[str]
    """
    if not os.path.isdir(folder):
        raise NotADirectoryError(f"Provided path is not a directory: {folder}")

    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and os.path.splitext(f)[-1].lower() == extension]
    return files

def get_pykrait_version() -> str:
    """returns the current version of pykrait."""
    try:
        __version__ = version("pykrait")
        return __version__
    except Exception as e:
        print(f"Could not retrieve pykrait version: {e}")
        return None  # Default version if not found