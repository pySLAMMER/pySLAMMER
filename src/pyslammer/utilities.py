import csv
import importlib.resources as pkg_resources

import numpy as np

from .ground_motion import GroundMotion

G_EARTH = 9.80665

__all__ = [
    "csv_time_hist",
    "sample_ground_motions",
    "load_sample_ground_motion",
    "psfigstyle",
]

psfigstyle = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial"],
    # "axes.labelweight": "bold",
    "axes.titleweight": "bold",
    "axes.formatter.use_mathtext": True,
    "legend.framealpha": 1.0,
    "legend.edgecolor": "white",
    # "mathtext.default": "regular",
    # "figure.dpi": 300,
}


def load_sample_ground_motion(filename: str) -> GroundMotion:
    """
    Load a single sample ground motion by filename from the `sample_ground_motions` folder.

    Parameters
    ----------
    filename : str
        The filename of the ground motion CSV file (with or without .csv extension)

    Returns
    -------
    GroundMotion
        A `GroundMotion` object containing the time history data and metadata.

    Raises
    ------
    FileNotFoundError
        If the specified file is not found in the sample_ground_motions folder.
    """
    # Ensure filename has .csv extension
    if not filename.endswith(".csv"):
        filename += ".csv"

    # Get the path to the sample_ground_motions folder
    folder_path = pkg_resources.files("pyslammer") / "sample_ground_motions"
    file_path = folder_path / filename

    try:
        motion_name = filename[:-4]  # Remove .csv extension
        return GroundMotion(*csv_time_hist(str(file_path)), motion_name)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Ground motion file '{filename}' not found in sample_ground_motions folder"
        )


def sample_ground_motions():
    """
    Load sample ground motions from the `sample_ground_motions` folder.

    Returns
    -------
    dict
        A dictionary where keys are motion names (str) and values are `GroundMotion` objects
        containing the time history data and metadata.

    Notes
    -----
    This function reads all CSV files in the `sample_ground_motions` folder and creates
    `GroundMotion` objects for each file. The file name (without extension) is used as the
    key in the returned dictionary.
    """
    sgms = {}

    # Get the path to the sample_ground_motions folder
    folder_path = pkg_resources.files("pyslammer") / "sample_ground_motions"

    # Iterate over all files in the folder
    try:
        for file_path in folder_path.iterdir():
            if file_path.name.endswith(".csv"):
                motion_name = file_path.name[:-4]
                sgms[motion_name] = load_sample_ground_motion(motion_name)
    except AttributeError:
        # Fallback for older Python versions
        import os

        folder_str = str(folder_path)
        for filename in os.listdir(folder_str):
            if filename.endswith(".csv"):
                motion_name = filename[:-4]
                sgms[motion_name] = load_sample_ground_motion(motion_name)

    return sgms


def csv_time_hist(filename: str):
    """
    Read a CSV file containing time history acceleration data and return a 1D numpy array and a timestep

    Returns:
        a_in: A 1D numpy array containing time history data.
        dt: The timestep of the data.
    """
    file = open(filename, "r")
    if file is None:
        return None
    else:
        pass
    reader = csv.reader(file)
    time = []
    accel = []
    for row in reader:
        if "#" in row[0]:
            continue
        else:
            pass
        if len(row) == 2:
            time.append(float((row[0])))
            accel.append(float((row[1])))
        else:
            accel.append(float((row[0])))
    dt = time[1] - time[0]
    accel = np.array(accel)
    return accel, dt
