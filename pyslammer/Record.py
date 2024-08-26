import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as spint

G_EARTH = 9.80665 # Acceleration due to gravity (m/s^2).


class Record():

    def __init__(self, gnd_motion: np.ndarray=[], name: str='None'):
        if len(gnd_motion) == 0:
            self.name = 'Empty Record'
            self.dt = -1.0
            self.pga = 0.0
        else:
            self.name = name
            self.gnd_motion = gnd_motion
            self.time = gnd_motion[0][:]
            self.dt = self.time[1] - self.time[0]
            self._calc_gnd_params()

    def __str__(self):
        if self.dt == -1.0:
            info = ('Record: {}\n'.format(self.name))
        else:
            info = ('Record: {}\n'.format(self.name)
                    +'PGA   : {:.3f} g\n'.format(self.pga)
                    +'dt    : {:.3f} s'.format(self.dt))
        return info
    
    def plot(self, acc=True, vel=True, disp=True):
        if self.dt == -1.0:
            return
        num_plots = sum([acc, vel, disp])
        remain_plots = num_plots
        if num_plots == 1:
            fig, ax = plt.subplots(figsize=(10, 10))
        else:
            fig, ax = plt.subplots(num_plots, 1, figsize=(10, 10))
        if acc:
            if num_plots == 1:
                acc = ax
            else:
                i = num_plots - remain_plots
                remain_plots -= 1
                acc = ax[i]
            acc.plot(self.time, self.gnd_acc, label='Ground Acceleration')
            acc.set_ylabel('Acceleration (m/s^2)')
            acc.set_title('Ground Acceleration')
            acc.legend()
        if vel:
            if num_plots == 1:
                vel = ax
            else:
                j = num_plots - remain_plots
                remain_plots -= 1
                vel = ax[j]
            vel.plot(self.time, self.gnd_vel, label='Ground Velocity')
            vel.set_ylabel('Velocity (m/s)')
            vel.set_title('Ground Velocity')
            vel.legend()
        if disp:
            if num_plots == 1:
                disp = ax
            else:
                k = num_plots - remain_plots
                remain_plots -= 1
                disp = ax[k]
            disp.plot(self.time, self.gnd_disp, label='Ground Displacement')
            disp.set_xlabel('Time (s)')
            disp.set_ylabel('Displacement (m)')
            disp.set_title('Ground Displacement')
            disp.legend()
        plt.show()
    
    def _calc_gnd_params(self):
        self.gnd_acc = self.gnd_motion[1][:] * G_EARTH
        self.gnd_vel = spint.cumulative_trapezoid(self.gnd_acc, self.time, initial=0)
        self.gnd_disp = spint.cumulative_trapezoid(self.gnd_vel, self.time, initial=0)
        self.inv_gnd_acc = -1 * self.gnd_acc
        self.inv_gnd_vel = spint.cumulative_trapezoid(self.inv_gnd_acc, self.time, initial=0)
        self.inv_gnd_disp = spint.cumulative_trapezoid(self.inv_gnd_vel, self.time, initial=0)
        self.pga = max(abs(self.gnd_acc)) / G_EARTH
        self.is_scaled = False
    
    def scale(self, pga: float=None):
        """
        Scale the ground motion using desired method.
        Args:
            pga (float, optional): Desired peak ground acceleration in g.
        Returns: 
            None
        """
        if pga is not None:
            scale_factor = pga / self.pga
            self.gnd_acc *= scale_factor
            self.gnd_vel *= scale_factor
            self.gnd_disp *= scale_factor
            self.inv_gnd_acc *= scale_factor
            self.inv_gnd_vel *= scale_factor
            self.inv_gnd_disp *= scale_factor
            self.pga = pga
        self.is_scaled = True
        self.name = self.name + '_SCALED'

    def unscale(self):
        """
        Unscale the ground motion.
        Args:
            None
        Returns:
            None
        """
        self._calc_gnd_params()