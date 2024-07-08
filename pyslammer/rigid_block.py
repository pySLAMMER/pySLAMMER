# Rigid Block Analysis

import numpy as np
import scipy.integrate as spint

G_EARTH = 9.80665 # Acceleration due to gravity (m/s^2).


def downslope_analysis_jibson(time_history: np.ndarray, acc_crit: float):
    """
    Perform downslope analysis using Jibson's 1993 method.

    Parameters:
    - time_history (numpy.ndarray): Array containing time (s) and acceleration (g's) data.
    - acc_crit (float): Critical acceleration value in multiples of g.

    Returns:
    - block_data (numpy.ndarray): Array containing time (s), displacement (m), and velocity (m/s) data.
    """
    if time_history is None:
        return
    else:
        pass
    acc_crit = acc_crit * G_EARTH
    time = time_history[0][:]
    gnd_acc = time_history[1][:]
    block_disp = []
    block_vel = []
    block_acc = []
    tol = 0.00001
    dt = time[1] - time[0]  # D
    pos_curr = 0  # U
    vel_curr = 0  # V
    pos_prev = 0  # Q
    vel_prev = 0  # R
    acc_prev = 0  # S
    acc_curr = 0  # Y
    for i in range(len(gnd_acc)):
        gnd_acc_curr = gnd_acc[i]
        if vel_curr < tol:
            if abs(gnd_acc_curr) > acc_crit:
                n = gnd_acc_curr / abs(gnd_acc_curr)
            else:
                n = gnd_acc_curr / acc_crit
        else:
            n = 1
        acc_curr = gnd_acc_curr - n * acc_crit
        vel_curr = vel_prev + (dt / 2) * (acc_curr + acc_prev)
        if vel_curr > 0:
            pos_curr = pos_prev + (dt / 2) * (vel_curr + vel_prev)
        else:  # P
            vel_curr = 0
            acc_curr = 0
        pos_prev = pos_curr
        vel_prev = vel_curr
        acc_prev = acc_curr
        block_disp.append(pos_curr)
        block_vel.append(vel_curr)
        block_acc.append(acc_curr)
    block_data = np.vstack((time, block_disp, block_vel))
    return block_data


def downslope_analysis_dgr(time_history: np.ndarray, acc_crit: float):
    """
    Perform downslope analysis using Garcia-Rivas' method.

    Parameters:
    - time_history (numpy.ndarray): Array containing time and acceleration (g's) data.
    - acc_crit (float): Critical acceleration value in multiples of g.

    Returns:
    - block_data (numpy.ndarray): Array containing time (s), displacement (m), and velocity (m/s) data.
    """

    if time_history is None:
        return
    else:
        pass
    acc_crit = acc_crit * G_EARTH
    time = time_history[0][:]
    dt = time[1]-time[0]
    gnd_acc = time_history[1][:]
    gnd_vel = spint.cumulative_trapezoid(gnd_acc, time, initial=0)
    block_vel = np.copy(gnd_vel)
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
    relative_vel = abs(gnd_vel - block_vel)
    block_disp = spint.cumulative_trapezoid(relative_vel, time, initial=0)
    block_data = np.vstack((time, block_disp, relative_vel))
    return block_data