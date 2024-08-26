import numpy as np
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