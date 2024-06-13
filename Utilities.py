from math import pi
import tkinter.filedialog as tkf
import tkinter.simpledialog as dlg
import numpy as np
import csv

G_EARTH = 9.80665


def select_csv():
    """
    Open a file dialog to select a time history CSV file.

    Returns:
    file: The selected file.
    """
    file = tkf.askopenfilenames(title='Select a Time History CSV File')
    return file


def csv_time_hist(filename):
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
        dt = dlg.askfloat('Enter dt', 'Enter a time interval (s): ')
        time = np.arange(0, len(accel)*dt, dt)
    else:
        pass
    time = np.array(time)
    accel = np.array(accel) * G_EARTH
    time_history = np.vstack((time, accel))
    return time_history


def test_time_hist():
    """
    Prompts the user to enter a time interval and desired frequency,
    and generates a time history array based on the input.

    Returns:
    time_history (ndarray): A 2D array containing time and acceleration values.
    """
    while True:
        time_interval = input('Enter dt (s): ')
        try:
            time_interval = float(time_interval)
            break
        except ValueError:
            print('Enter a valid time interval.')
    while True:
        freq = input('Enter desired frequency (Hz): ')
        try:
            freq = float(freq)*2*pi
            break
        except ValueError:
            print('Enter a valid frequency.')
    time = np.arange(0, 30, time_interval) 
    accel = np.sin(freq*time) * G_EARTH
    time_history = np.vstack((time, accel))
    return time_history