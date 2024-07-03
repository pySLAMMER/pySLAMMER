from pyslammer.rigid_block import *
from pyslammer.utilities import csv_time_hist

import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate as spint

G_EARTH = 9.80665 # TODO: consolidate to constants file and better document what units are being used different places.

class SlidingBlockAnalysis:
    def __init__(self, time_hist, ky, analysis_type = "rigid",  method = "jibson"):
        # Initialize attributes here
        self.analysis_types = {
            "rigid": self.rigid_analysis,
            "decoupled": self.decoupled_analysis,
            "coupled": self.coupled_analysis,
        }

        self.method = None
        self.ky = None
        self.time = None

        self.ground_acc = None
        self.ground_vel = None
        self.ground_disp = None
        
        self.block_acc = None
        self.block_vel = None
        self.block_disp = None

        self.sliding_vel = None
        self.sliding_disp = None
        self.max_sliding_disp = None

        analysis_function = self.analysis_types.get(analysis_type)
        if analysis_function:
            analysis_function(time_hist, ky, method)
        else:
            print(f"Analysis type {analysis_type} is not supported.")
        pass

    def __str__(self):
        # Return a string representation of the object
        return "SlidingBlockResult"

    def rigid_analysis(self, time_hist, ky, method = "jibson"):
        """
        Perform downslope analysis using the specified method.

        Parameters:
        - time (numpy.ndarray): Array containing time and acceleration data.
        - ky (float): Stiffness value in kN/m.
        - method (str): Method to use for analysis. by default "jibson".

        Returns:
        - result (SlidingBlockResult): Object containing analysis results.
        """
        self.method = method
        self.ky = ky
        self.time = time_hist[0]
        self.ground_acc = time_hist[1]
        self.ground_vel = spint.cumulative_trapezoid(self.ground_acc, self.time, initial=0)
        self.ground_disp = spint.cumulative_trapezoid(self.ground_vel, self.time, initial=0)
        
        if self.method == "jibson":
            result = downslope_analysis_jibson(time_hist, ky)
            self.sliding_disp = result[1]
            self.sliding_vel = result[2]
            
            self.block_vel = self.ground_vel - self.sliding_vel
        elif self.method == "dgr":
            result = downslope_analysis_dgr(time_hist, ky)
            self.sliding_disp = result[1]
            self.block_vel = result[2]

            self.sliding_vel = self.ground_vel - self.block_vel
        else:
            result = None
            print(f"{self.method} is an invalid method. Please use 'jibson' or 'dgr'.")
        if result is not None:
            self.block_acc = np.where(abs(self.block_vel - self.ground_vel)>1e-10, G_EARTH*self.ky, self.ground_acc)
            self.block_disp = spint.cumulative_trapezoid(self.block_vel, self.time, initial=0)
            self.max_sliding_disp = np.max(self.sliding_disp)
            
        return None

    def decoupled_analysis(self):
        print("Sorry, decoupled analysis is not yet implemented.")
        pass

    def coupled_analysis(self):
        print("Sorry, coupled analysis is not yet implemented.")
        pass

def sliding_block_plot(sliding_block_result, sliding_vel_mode = True, fig = None):
    bclr = "k"
    gclr = "tab:blue"
    kyclr = "k"
    sbr = sliding_block_result
    if fig is None: #gAcc,gVel,bVel,bDisp,t,ky):
        fig, axs = plt.subplots(3,1,sharex=True)
    else:
        axs = fig.get_axes()

    axs[0].plot(sbr.time, G_EARTH*sbr.ky*np.ones(len(sbr.time)), label='Yield Acceleration', linestyle='--', color=kyclr, linewidth=0.5)
    axs[0].plot(sbr.time, sbr.ground_acc, label='Ground Acceleration', color=gclr)
    axs[0].plot(sbr.time, sbr.block_acc, label='Block Acceleration', color=bclr)
    axs[0].set_ylabel('Acceleration (m/s^2)')
    axs[0].set_xlim([sbr.time[0], sbr.time[-1]])

    if sliding_vel_mode:
        axs[1].plot(sbr.time, sbr.sliding_vel, label='Sliding Velocity', color=bclr)
    else:
        axs[1].plot(sbr.time, sbr.ground_vel, label='Ground Velocity', color=gclr)
        axs[1].plot(sbr.time, sbr.block_vel, label='Block Velocity', color=bclr)
    axs[1].set_ylabel('Velocity (m/s)')

    axs[2].plot(sbr.time, sbr.sliding_disp, label='Block Displacement', color=bclr)
    axs[2].set_ylabel('Displacement (m)')
    for i in range(len(axs)):
        axs[i].set_xlabel("Time (s)")
        axs[i].grid(which='both')
        # Place the legend outside the plot area
        axs[i].legend(loc='upper left', bbox_to_anchor=(1, 1))
    fig.tight_layout()
    fig.canvas.toolbar_position = 'top'
    return fig, axs