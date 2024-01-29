import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

fs = 22500 # Test sample frequency.
dt = 1/fs # Time interval between samples.
aCrit = 0.5 # Critical acceleration (G). 

# Time (t) and acceleration (a) arrays.
t = np.arange(0,10,dt)
aInput = np.sin(0.5*t)

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

# Creates an array of relative acceleration where negative values (those less than aCrit) are normalized to zero.
aOutput = aInput - aCrit
for i in range(len(aOutput)):
    if ( aOutput[i] > 0 ):
        continue
    else:
        aOutput[i] = 0

velocity = integrate(aOutput,dt)    
disp = integrate(velocity,dt)

# Plotting to examine output.
fig, ax = plt.subplots()
ax.plot(t, aInput, label='Acceleration')
ax.plot(t, aOutput, label='Exceedance')
ax.plot(t, velocity, label='Velocity')
ax.plot(t, disp, label='Displacement')
ax.set_xlabel("Time (s)")
ax.legend()
plt.show()
