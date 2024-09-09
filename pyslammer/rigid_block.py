import numpy as np
import scipy.integrate as spint
import matplotlib.pyplot as plt
from .record import Record

G_EARTH = 9.80665 # Acceleration due to gravity (m/s^2).


class RigidBlock(Record):
    """Rigid Block Analysis."""

    def __init__(self, gnd_motion: np.ndarray=[], name: str=''):
        """
        Creates a rigid block analysis object.
        Args:
            gnd_motion (np.ndarray): Ground motion record in time (row 0), acceleration (row 1) format.
            name (str): Name of the record.
        """
        super().__init__(gnd_motion, name)
        self._clear_block_params()

    def __str__(self):
        if self.dt == -1.0:
            info = ('Record: {}\n'.format(self.name))
        else:
            info = (
                    'Rigid Block Analysis\n'
                    +'Record  : {}\n'.format(self.name)
                    +'PGA     : {:.3f} g\n'.format(self.pga)
                    +'dt      : {:.3f} s\n'.format(self.dt)
                    +'k_y     : {:.3f} m/s^2\n'.format(self.k_y)
                    +'Disp    : {:.3f} m'.format(self.total_disp)
                )
        return info
    
    def _clear_block_params(self):
        """
        Semi-private method to initialize and clear block parameters.
        Args:
            None
        Creates:
            k_y (float): Critical acceleration (m/s^2).
            block_acc (list): Block acceleration (m/s^2).
            block_vel (list): Block differential velocity (m/s).
            block_disp (list): Block displacement (m).
            total_disp (float): Total block displacement (m).
        """
        self.k_y = 0.0
        self.block_acc = []
        self.block_vel = []
        self.block_disp = []
        self.total_disp = 0.0

    def downslope_jibson(self, k_y: float=0.0):
        """
        Calculate the downslope rigid block displacement, differential velocity, and acceleration using the Jibson method.
        Args:
            k_y (float, optional): Critical acceleration in multiples of g.
        Returns:
            None
        """
        if self.dt == -1.0:
            return
        else:
            self._clear_block_params()
            tol = 0.00001
            self.k_y = k_y * G_EARTH

        # [previous, current]
        acc = [0, 0]
        vel = [0, 0]
        pos = [0, 0]

        for i in range(len(self.gnd_acc)):
            gnd_acc_curr = self.gnd_acc[i]
            if vel[1] < tol:
                if abs(gnd_acc_curr) > self.k_y:
                    n = gnd_acc_curr / abs(gnd_acc_curr)
                else:
                    n = gnd_acc_curr / self.k_y
            else:
                n = 1
            acc[1] = gnd_acc_curr - n * self.k_y
            vel[1] = vel[0] + (self.dt / 2) * (acc[1] + acc[0])
            if vel[1] > 0:
                pos[1] = pos[0] + (self.dt / 2) * (vel[1] + vel[0])
            else:
                vel[1] = 0
                acc[1] = 0
            pos[0] = pos[1]
            vel[0] = vel[1]
            acc[0] = acc[1]
            self.block_disp.append(pos[1])
            self.block_vel.append(vel[1])
            self.block_acc.append(acc[1])
            self.total_disp = self.block_disp[-1]

    def downslope_dgr(self, k_y: float=0.0):
        """
        Calculate the downslope rigid block displacement, differential velocity, and acceleration using the Jibson method.
        Args:
            k_y (float, optional): Critical acceleration in multiples of g.
        Returns:
            None
        """
        if self.dt == -1.0:
            return
        else:
            self._clear_block_params()
            self.k_y = k_y * G_EARTH
        block_sliding = False
        for i in range(len(self.gnd_acc)):
            if i == 0:
                self.block_acc.append(self.gnd_acc[i])
                self.block_vel.append(self.gnd_vel[i])
                continue
            tmp_block_vel = self.block_vel[i-1] + self.k_y*self.dt
            if self.gnd_acc[i] > self.k_y:
                block_sliding = True
            elif tmp_block_vel > self.gnd_vel[i]:
                block_sliding = False
            else:
                pass
            if block_sliding == True:
                self.block_vel.append(tmp_block_vel)
                self.block_acc.append(self.k_y)
            else:
                self.block_acc.append(self.gnd_acc[i])
                self.block_vel.append(self.gnd_vel[i])
        self.block_vel = abs(self.gnd_vel - self.block_vel)
        self.block_disp = spint.cumulative_trapezoid(self.block_vel, self.time, initial=0)
        self.total_disp = self.block_disp[-1]

    def plot(self, acc: bool=True, vel: bool=True, disp: bool=True, gnd_motion: bool=False):
        """
        Plot the ground motion and the block response.
        Args:
            acc (bool, optional): Plot block acceleration.
            vel (bool, optional): Plot block differential velocity.
            disp (bool, optional): Plot block displacement.
            gnd_motion (bool, optional): Plot ground motion.
        Returns:
            None
        """
        num_plots = sum([acc, vel, disp])
        if self.dt == 1.0:
            return
        elif num_plots == 0:
            return
        elif len(self.block_acc) == 0:
            if gnd_motion:
                super().plot(acc, vel, disp, gnd_motion, called=False)
                return
            else:
                return
        else:
            pass
        fig, ax = super().plot(acc, vel, disp, gnd_motion, called=True)
        fig.suptitle('Rigid Block Analysis\n{}'.format(self.name))
        remain_plots = num_plots
        if acc:
            if num_plots == 1:
                acc = ax
            else:
                i = num_plots - remain_plots
                remain_plots -= 1
                acc = ax[i]
            acc.plot(self.time, self.block_acc, label='Block Acceleration')
            acc.plot(self.time, [self.k_y for i in range(len(self.time))], label='Critical Acceleration')
            acc.legend()
        if vel:
            if num_plots == 1:
                vel = ax
            else:
                j = num_plots - remain_plots
                remain_plots -= 1
                vel = ax[j]
            vel.plot(self.time, self.block_vel, label='Block Differential Velocity')
            vel.legend()
        if disp:
            if num_plots == 1:
                disp = ax
            else:
                k = num_plots - remain_plots
                remain_plots -= 1
                disp = ax[k]
            disp.plot(self.time, self.block_disp, label='Block Displacement')
            disp.legend()
        plt.show()