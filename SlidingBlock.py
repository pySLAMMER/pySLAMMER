# Sliding Block Analysis

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import tkinter.filedialog as tkf
import csv

# timeHistFile = tkf.askopenfile(mode='r',title='Select a Time History') # IN PROGRESS
# thf = csv.reader(timeHistFile) # IN PROGRESS

fs = 22500 # Test sample frequency (Hz).
dt = 1/fs # Time interval between samples (s).
aCrit = 0.5 # Critical acceleration (G). 

# Time (t) and ground acceleration (gAcc) arrays.
t = np.arange(0,20,dt)
gAcc = 2*np.sin(t)

# This function performs a trapezoid rule integration of the input array and returns the result as an array
# of the same size and type as the input. The first interation is skipped to prevent a zero width trapezoid.
def integrate(input,step):
    output = np.zeros_like(input)
    for i in range(len(input)):
        if i == 0:
            continue
        else:
            output[i] = output[i-1] + 0.5*(input[i]+input[i-1])*step
    return output

# Determine ground velocity (gVel) and displacement (gDisp).
gVel = integrate(gAcc,dt)    
# gDisp = integrate(gVel,dt) # Probably don't need this.

# Determine block velocity (bVel) and provide a relative velocity (rVel) array for displacement calculation.
bVel = np.copy(gVel)
rVel = np.zeros_like(gVel)
blockSliding = False # Logic flag to determine if the block is sliding.
for i in range(len(gAcc)):
    if gAcc[i] > aCrit:
        blockSliding = True
    tVel = bVel[i-1] + aCrit*dt # Temporary velocity value assuming the block is sliding with acceleration aCrit.
    if tVel > gVel[i]: # Ends block sliding if block velocity matches ground velocity.
        blockSliding = False
        continue
    else:
        bVel[i] = tVel
        rVel[i] = gVel[i] - tVel

# Determine block accumulated displacement based on relative velocity array.        
bDisp = integrate(rVel,dt)
        
# Plotting to examine output.
fig, ax = plt.subplots()
ax.plot(t, gAcc, label='Ground Acceleration')
ax.plot(t, gVel, label='Ground Velocity')
# ax.plot(t, gDisp, label='Ground Displacement') # Probably don't need this.
ax.plot(t, bVel, label='Block Velocity')
ax.plot(t, bDisp, label='Block Displacement')
ax.set_xlabel("Time (s)")
ax.legend()
plt.show()