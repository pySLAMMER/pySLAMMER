# Sliding Block Analysis
# Jibson 1993 BASIC conversion

from math import pi
import numpy as np
# import matplotlib as mpl
# import matplotlib.pyplot as plt
import tkinter.filedialog as tkf
import csv

G_EARTH = 9.80665
M_TO_CM = 100


def read_csv():
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


def time_integrate(output_dot, dt):
    output = np.zeros_like(output_dot)
    for i in range(len(output_dot)):
        if i == 0:
            continue
        else:
            output[i] = output[i-1] + 0.5*(output_dot[i] + output_dot[i-1])*dt
    return output


def downslope_analysis_jibson(time_history):
    if time_history is None:
        return
    else:
        pass
    time = time_history[0][:]
    gnd_acc = time_history[1][:]
    block_disp = []
    block_vel = []
    block_acc = []
    tol = 0.00001
    while True:
        acc_crit = input('Enter critical acceleration (g): ') # T
        try:
            acc_crit = float(acc_crit) * G_EARTH
            break
        except ValueError:
            print('Enter a valid number.')
    dt = time[1]-time[0] # D
    pos_curr = 0 # U
    vel_curr = 0 # V
    pos_prev = 0 # Q
    vel_prev = 0 # R
    acc_prev = 0 # S
    acc_curr = 0 # Y
    for i in range(len(gnd_acc)):
        gnd_acc_curr = gnd_acc[i]
        if vel_curr < tol:
            if abs(gnd_acc_curr) > acc_crit:
                n = gnd_acc_curr/abs(gnd_acc_curr)
            else:
                n = gnd_acc_curr/acc_crit
        else:
            n = 1
        acc_curr = gnd_acc_curr - n*acc_crit
        vel_curr = vel_prev + (dt/2) * (acc_curr+acc_prev)
        if vel_curr > 0:
            pos_curr = pos_prev + (dt/2) * (vel_curr+vel_prev)
        else: # P
            vel_curr = 0
            acc_curr = 0
        pos_prev = pos_curr
        vel_prev = vel_curr
        acc_prev = acc_curr
        block_disp.append(pos_curr)
        block_vel.append(vel_curr)
        block_acc.append(acc_curr)
    print('Displacement: '+'{:.4f}'.format(block_disp[-1]*M_TO_CM)+' cm')
    block_data = np.vstack((time, block_disp, block_vel))
    return block_data


def downslope_analysis_dgr(time_history):
        if time_history is None:
            return
        else:
            pass
        time = time_history[0][:]
        dt = time[1]-time[0]
        gnd_acc = time_history[1][:]
        while True:
            acc_crit = input('Enter critical acceleration (g): ') # T
            try:
                acc_crit = float(acc_crit) * G_EARTH
                break
            except ValueError:
                print('Enter a valid number.')
        gnd_vel = time_integrate(gnd_acc, dt)
        block_vel = np.copy(gnd_vel)
        block_acc = []
        block_sliding = False
        for i in range(len(gnd_acc)):
            if i == 0:
                continue
            tmp_block_vel = block_vel[i-1] + acc_crit*dt
            if gnd_acc[i] > acc_crit:
                block_sliding = True
            elif tmp_block_vel > gnd_vel[i]:
                block_sliding = False
            else:
                pass
            if block_sliding == True:
                block_vel[i] = tmp_block_vel
            else:
                continue
        relative_vel = gnd_vel - block_vel
        block_disp = time_integrate(relative_vel, dt)
        print('Displacement: '+'{:.4f}'.format(block_disp[-1]*M_TO_CM)+' cm')
        block_data = np.vstack((time, block_disp, block_vel))
        return block_data

while True:
    downslope_analysis_jibson(read_csv())
    if input('Continue? (y/n): ') == 'n':
        break