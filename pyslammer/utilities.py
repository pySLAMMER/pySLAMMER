from pathlib import Path
import os
# import tkinter.filedialog as tkf
# import tkinter.simpledialog as dlg
import numpy as np
import datetime as dtm
import csv

G_EARTH = 9.80665

__all__ = ['csv_time_hist', 'sample_ground_motions']


def sample_ground_motions():
    sgms = {}

    # Get the path to the sample_ground_motions folder
    folder_path = Path(__file__).resolve().parent / "sample_ground_motions"

    # Iterate over all files in the folder
    for file_path in folder_path.glob("*.csv"):
        # Add the file name to the list
        sgms[file_path.name[:-4]] = csv_time_hist(file_path)

    return sgms


def csv_time_hist(filename: str):
    """
    Read a CSV file containing time history data and return it as a numpy array.

    Returns:
        numpy.ndarray: A 2D numpy array containing time history data.
            The first row represents time values, and the second row represents acceleration values.
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
    if len(time) == 0:
        dt = dlg.askfloat('Enter dt', 'Enter a time interval (block_disp): ')
        time = np.arange(0, len(accel)*dt, dt)
    else:
        pass
    time = np.array(time)
    accel = np.array(accel) * G_EARTH
    time_history = np.vstack((time, accel))
    return time_history