# Sliding Block Analysis

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import tkinter.filedialog as tkf
import csv

timeHistFile = tkf.askopenfile(mode='r',title='Select a Time History')
thf = csv.reader(timeHistFile)

# Time (t) and ground acceleration (gAcc) arrays are created as empty python lists and later are
# converted to numpy arrays after csv parsing is complete. This allows array creation without 
# knowing length.
t = []
gAcc = []

# For loop to parse acceleration time history csv file. Ignores header data containing '#' and
# assumes row format is [time,acceleration].
for row in thf:
    if '#' in row[0]:
        continue
    t.append(float((row[0])))
    gAcc.append(float((row[1])))

t = np.array(t)
gAcc = np.array(gAcc)

dt = t[1]-t[0] # Time interval between samples (s).
fs = 1/dt # Sample frequency (Hz).
aCrit = float(input('Enter critical acceleration (g): ')) # User input critical acceleration (g)

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

# Determine block accumulated displacement (bDisp) based on relative velocity array.        
bDisp = integrate(rVel,dt)
        
# Plotting to examine output.
fig, ax = plt.subplots()
ax.plot(t, gAcc, label='Ground Acceleration')
ax.plot(t, gVel, label='Ground Velocity')
ax.plot(t, bVel, label='Block Velocity')
ax.plot(t, bDisp, label='Block Displacement')
ax.set_xlabel("Time (s)")
ax.legend()
plt.show()