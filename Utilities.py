from math import pi
import tkinter.filedialog as tkf
import numpy as np
import csv

G_EARTH = 9.80665


def csv_time_hist():
    file = tkf.askopenfile(mode='r', title='Select a Time History')
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
        time.append(float((row[0])))
        accel.append(float((row[1])))
    time = np.array(time)
    accel = np.array(accel) * G_EARTH
    time_history = np.vstack((time, accel))
    return time_history


def test_time_hist():
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