import csv
import importlib.resources as pkg_resources

import numpy as np

from pyslammer.record import GroundMotion

G_EARTH = 9.80665

__all__ = ["csv_time_hist", "sample_ground_motions", "psfigstyle"]

psfigstyle = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial"],
    # "axes.labelweight": "bold",
    "axes.titleweight": "bold",
    "axes.formatter.use_mathtext": True,
    # "mathtext.default": "regular",
    # "figure.dpi": 300,
}


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
    for file_path in folder_path.glob("*.csv"):
        # Add the file name to the list
        motion_name = file_path.name[:-4]
        sgms[motion_name] = GroundMotion(*csv_time_hist(file_path), motion_name)

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
