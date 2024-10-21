import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate as spint

from pyslammer.constants import G_EARTH


class SlidingBlockAnalysis:

    def __init__(self):
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
        self._npts = None
        pass

    def tbd(self):
        time = np.arange(0, self._npts * self.dt, self.dt)
        if self.ground_vel is None:
            self.ground_vel = spint.cumulative_trapezoid(self.ground_acc, time, initial=0)
            self.ground_disp = spint.cumulative_trapezoid(self.ground_vel, time, initial=0)
        if self.sliding_vel is None:
            self.sliding_vel = self.ground_vel - self.block_vel
        if self.sliding_disp is None:
            self.sliding_disp = self.block_disp# - self.ground_disp
        pass

    def sliding_block_plot(self, sliding_vel_mode=True, fig=None):
        self.tbd()
        bclr = "k"
        gclr = "tab:blue"
        kyclr = "k"
        if fig is None:  # gAcc,gVel,bVel,bDisp,t,ky):
            fig, axs = plt.subplots(3, 1, sharex=True)
            fig.set_size_inches(10, 6)
        else:
            axs = fig.get_axes()
        time = np.arange(0, self._npts * self.dt, self.dt)

        # axs[0].plot(time, self.ky * np.ones(len(time))/G_EARTH, label='Yield Acc.', linestyle='--',
        #             color=kyclr, linewidth=0.5)
        axs[0].plot(time, self.ground_acc/G_EARTH, label='Ground Acc.', color=gclr)
        axs[0].plot(time, self.block_acc/G_EARTH, label='Block Acc.', color=bclr)
        axs[0].set_ylabel('Acc. (g)')
        axs[0].set_xlim([time[0], time[-1]])

        if sliding_vel_mode:
            axs[1].plot(time, self.sliding_vel, label='Sliding Vel.', color=bclr)
        else:
            axs[1].plot(time, self.ground_vel, label='Ground Vel.', color=gclr)
            axs[1].plot(time, self.block_vel, label='Block Vel.', color=bclr)
        axs[1].set_ylabel('Vel. (m/s)')

        axs[2].plot(time, self.sliding_disp, label='Sliding Disp.', color=bclr)
        axs[2].set_ylabel('Disp. (m)')
        for i in range(len(axs)):
            axs[i].set_xlabel("Time (s)")
            axs[i].grid(which='both')
            # Place the legend outside the plot area
            axs[i].legend(loc='upper left', bbox_to_anchor=(1, 1))
        fig.tight_layout()
        fig.canvas.toolbar_position = 'top'
        return fig, axs



