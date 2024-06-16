# Sliding Block Analysis

from math import pi
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import csv

g = 9.80665 # Acceleration due to gravity (m/s^2).

############# FUNCTIONS #############

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

def vel_verlet(acc,dt):
    vel = np.zeros_like(acc)
    pos = np.zeros_like(acc)
    for i in range(len(acc)-1):
        vel_half_step = vel[i]+0.5*acc[i]*dt
        pos[i+1] = pos[i]+vel_half_step*dt
        vel[i+1] = vel_half_step+0.5*acc[i+1]*dt
    return(vel)

# This function determines absolute block velocity based on ground velocity and whether or not ground
# acceleration is greater than critical acceleration.
def blockVelocity(gVel,gAcc,aCrit,dt):
    bVel = np.copy(gVel)
    blockSliding = False # Logic flag to determine if the block is sliding.
    for i in range(len(gAcc)):
        tVel = bVel[i-1] + aCrit*dt # Temporary velocity value assuming the block is sliding with acceleration aCrit.
        if gAcc[i] > aCrit:
            blockSliding = True
        elif tVel >= gVel[i]: # Ends block sliding if block velocity matches ground velocity.
            blockSliding = False
        else:
           pass
        if blockSliding == True:
            bVel[i] = tVel
        else:
            pass
    return bVel

# Plotting to examine output.
def plotOutput(gAcc,gVel,bVel,bDisp,t,ky):
    fig, axs = plt.subplots(3,1,sharex=True)
    axs[0].plot(t, gAcc/g, label='Ground Acceleration')
    axs[0].plot(t, ky*np.ones(len(t)), label='Yield Acceleration', linestyle='--', color='black', linewidth=0.5)
    axs[0].set_ylabel('Acceleration (g)')
    axs[1].plot(t, gVel*100, label='Ground Velocity')
    axs[1].plot(t, bVel*100, label='Block Velocity')
    axs[1].set_ylabel('Velocity (cm/s)')
    axs[2].plot(t, bDisp*100, label='Block Displacement')
    axs[2].set_ylabel('Displacement (cm)')
    for i in range(len(axs)):
        axs[i].set_xlabel("Time (s)")
        # axs[i].legend()
        axs[i].grid(which='both')
    fig.canvas.toolbar_position = 'top'
    return fig, axs

def downslopeAnalysis(tHist,aCrit):
    t = tHist[0,:]
    gAcc = tHist[1,:]
    dt = t[1]-t[0] # Time interval between samples (s).
    # gVel = integrate(gAcc,dt) # Determine ground velocity (gVel).
    gVel = vel_verlet(gAcc,dt)
    bVel = blockVelocity(gVel,gAcc,aCrit,dt) # Determine block velocity (bVel)

    # Determine block accumulated displacement (bDisp) based on relative velocity (rVel).
    rVel = gVel - bVel        
    bDisp = integrate(rVel,dt)
    total_disp = bDisp[-1]*100
    # print(f'{total_disp = :.3f} cm')
    return gAcc, gVel, bVel, bDisp, t 

def normModeTimeHist(timeHistFile):
    # timeHistFile = tkf.askopenfile(mode='r',title='Select a Time History')
    with open(timeHistFile) as input_file:
        thf = csv.reader(input_file)

        # Time (t) and ground acceleration (gAcc) arrays are created as empty python lists and later are
        # converted to numpy arrays after csv parsing is complete. This allows array creation without 
        # knowing length.
        t = []
        gAcc = []      

        # For loop to parse acceleration time history csv file. Ignores header data containing '#' and
        # assumes row format is [time,acceleration]. Reads row and appends values of time and acceleration
        # respective array.
        for row in thf:
            if '#' in row[0]:
                continue
            t.append(float((row[0])))
            gAcc.append(float((row[1])))
        t = np.array(t)
        gAcc = np.array(gAcc) * g # Convert to m/s^2 for reasons.
        tHist = np.vstack((t,gAcc)) 
        return tHist



# def writeCSV(thf):
#     file = tkf.asksaveasfile(mode='w',title='Save Output',)
#     writer = csv.writer(file,delimiter=',')
#     for row in range(thf.shape[1]):
#         writer.writerow([thf[1,row]/g])
#     print('File save complete!')
    
############# MAIN LOOP #############
if __name__ == '__main__':
    pass

    