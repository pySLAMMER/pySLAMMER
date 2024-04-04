# Sliding Block Analysis
# Jibson 1993 BASIC conversion

from math import pi
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import tkinter.filedialog as tkf
import csv

G_EARTH = 9.80665
M_TO_CM = 100


def read_csv():
    file = tkf.askopenfile(mode='r', title='Select a Time History')
    reader = csv.reader(file)
    time = []
    accel = []
    for row in reader:
        if '#' in row[0]:
            continue
        time.append(float((row[0])))
        accel.append(float((row[1])))
    time = np.array(time)
    accel = np.array(accel) * G_EARTH
    time_history = np.vstack((time, accel))
    return time_history

def test_time_hist():
    time_interval = float(input('Enter dt (s): '))
    freq = float(input('Enter desired frequency (Hz): '))*2*pi
    time = np.arange(0, 30, time_interval) 
    accel = np.sin(freq*time) * G_EARTH
    time_history = np.vstack((time, accel))
    return time_history


def downslope_analysis(time_history):
    time = time_history[0][:]
    accel = time_history[1][:]
    block_disp = []
    tol = 0.00001
    a_crit = float(input('Enter critical acceleration (g): ')) * G_EARTH # T
    dt = time[1]-time[0] # D
    pos_curr = 0 # U
    vel_curr = 0 # V
    pos_prev = 0 # Q
    vel_prev = 0 # R
    s = 0 # S, possibly acc_prev
    y = 0 # Y, possibly acc_curr
    for i in range(len(accel)):
        loop_accel = accel[i]
        if vel_curr < tol:
            if abs(loop_accel) > a_crit:
                n = loop_accel/abs(loop_accel)
            else:
                n = loop_accel/a_crit
        else:
            n = 1
        y = loop_accel - n*a_crit
        vel_curr = vel_prev + (dt/2) * (y+s)
        if vel_curr > 0:
            pos_curr = pos_prev + (dt/2) * (vel_curr+vel_prev)
        else:
            vel_curr = 0
            y = 0
        pos_prev = pos_curr
        vel_prev = vel_curr
        s = y
        block_disp.append(pos_curr)
    print('Displacement: '+'{:.4f}'.format(block_disp[-1]*M_TO_CM)+' cm')


downslope_analysis(read_csv())
# downslope_analysis(test_time_hist())