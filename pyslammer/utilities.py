import importlib.resources as pkg_resources
from pathlib import Path
import numpy as np
import csv
from pyslammer.record import GroundMotion

G_EARTH = 9.80665

__all__ = ['csv_time_hist', 'sample_ground_motions']


def sample_ground_motions():
    sgms = {}

    # Get the path to the sample_ground_motions folder
    folder_path = pkg_resources.files('pyslammer') / "sample_ground_motions"

    # Iterate over all files in the folder
    for file_path in folder_path.glob("*.csv"):
        # Add the file name to the list
        sgms[file_path.name[:-4]] = GroundMotion(*csv_time_hist(file_path))

    return sgms


def csv_time_hist(filename: str):
    """
    Read a CSV file containing time history acceleration data and return a 1D numpy array and a timestep

    Returns:
        a_in: A 1D numpy array containing time history data.
        dt: The timestep of the data.
    """
    file = open(filename, 'r')
    if file is None:
        return None
    else:
        pass
    reader = csv.reader(file)
    time = []
    accel = []
    for row in reader:
        if '#' in row[0]:
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