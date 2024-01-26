import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

fs = 22500 # Sample frequency.
dt = 1/fs # Time interval between samples.
aCrit = 0.5 # Critical acceleration (G). 

# Time (t) and acceleration (a) arrays.
t = np.linspace(0, 10, 22500)
a = np.sin(0.5*t)

aOver = np.empty(len(a)) # Empty array to be filled with acceration data that exceeds critical acceleration.
for i in range(len(a)):
    if ( a[i] > aCrit ):
        aOver[i] = a[i]
    else:
        aOver[i] = 0

disp = np.empty(len(aOver)) # Empty displacement array to be filled.        
for i in range(len(aOver)):
    if (i == 0):
        disp[i] = 0
    elif (aOver[i] == 0):
        disp[i] = disp[i-1]
    else:
        disp[i] = disp[i-1] + 0.5*(aOver[i]+aOver[i-1])*(t[i]-t[i-1])
        

# Plotting to examine output.
fig, ax = plt.subplots()
ax.plot(t, a, label='Acceleration')
ax.plot(t, aOver, label='Exceedance')
ax.plot(t, disp, label='Displacement')
ax.set_xlabel("Time (s)")
ax.legend()
plt.show()
