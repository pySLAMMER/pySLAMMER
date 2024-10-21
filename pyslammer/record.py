import numpy as np
import pyslammer.constants as constants
import scipy.integrate as spint
from scipy.fft import rfft, rfftfreq
import matplotlib.pyplot as plt

#TODO: bring this into utilities.py

class GroundMotion():
    """Ground Motion Record."""
    def __init__(self, accel: np.ndarray or list, dt: float, name: str='None'):
        """
        Creates a ground motion record object.
        Args:
            acceleration (np.ndarray or list): Ground motion acceleration record in g
            dt (float): Time step of the record (s).
            name (str): Name of the record.
        Creates:
            _gnd_motion (np.ndarray): Copy of original ground motion record.
            _is_scaled (bool): True if the record is scaled.
            _is_inverted (bool): True if the record is inverted.
            name (str): Name of the record.
            time (np.ndarray): Time vector of the record (s).
            dt (float): Time step of the record (s).
        """
        self.accel = np.array(accel)
        self.dt = dt
        self.name = name
        self._is_inverted = False
        self._is_scaled = False
        self._npts = len(accel)
        self.pga = max(abs(accel))

        # FFT
        x = rfft(accel)[1::]
        freqs = rfftfreq(self._npts, dt)[1::]
        x_real = np.real(x)
        x_imag = np.imag(x)
        c = np.sqrt(x_real ** 2 + x_imag ** 2)

        self.mean_period = sum(c ** 2 / freqs) / sum(c ** 2)

    def __str__(self):
        return f"Ground Motion: {self.name}, PGA: {self.pga:.3f} g, dt: {self.dt:.3f} s, npts: {self._npts}"
    
    def _calc_gnd_params(self):
        """
        Semi-private method to initialize and recalculate ground motion parameters.
        Args:
            None
        Creates:
            gnd_acc (np.ndarray): Ground acceleration (m/s^2).
            gnd_vel (np.ndarray): Ground velocity (m/s).
            gnd_disp (np.ndarray): Ground displacement (m).
            pga (float): Peak ground acceleration in multiples of g.
        """
        self.gnd_acc = self._gnd_motion[1][:] * constants.G_EARTH
        self.gnd_vel = spint.cumulative_trapezoid(self.gnd_acc, self.time, initial=0)
        self.gnd_disp = spint.cumulative_trapezoid(self.gnd_vel, self.time, initial=0)
        self.pga = max(abs(self.gnd_acc)) / constants.G_EARTH
    
    def scale(self, pga: float=False, scale_factor: float=False):
        """
        Scale the ground motion using desired method. Does nothing if more than one method is selected.
        Args:
            pga (float, optional): Desired peak ground acceleration in g.
            scale_factor (float, optional): Desired scale factor.
        Returns: 
            None
        """
        if self.dt == -1.0:
            return
        else:
            pass
        if (pga and scale_factor):
            return
        else:
            if self._is_scaled:
                self.unscale()
            else:
                pass
        if pga:
            scale_factor = pga / self.pga
            self.gnd_acc *= scale_factor
            self.gnd_vel *= scale_factor
            self.gnd_disp *= scale_factor
            self.pga = pga
        elif scale_factor:
            self.gnd_acc *= scale_factor
            self.gnd_vel *= scale_factor
            self.gnd_disp *= scale_factor
            self.pga *= scale_factor
        else:
            return        
        self._is_scaled = True
        self.name = self.name + '_SCALED'

    def unscale(self):
        """
        Unscales the ground motion.
        Args:
            None
        Returns:
            None
        """
        if self.dt == -1.0:
            return
        else:
            pass
        self._calc_gnd_params()
        self.name = self.name.replace('_SCALED', '')

    def invert(self):
        """
        Invert the ground motion.
        Args:
            None
        Returns:
            None
        """
        if self.dt == -1.0:
            return
        else:
            pass
        if self._is_inverted:
            self.uninvert()
            return
        else:
            self.gnd_acc *= -1
            self.gnd_vel *= -1
            self.gnd_disp *= -1
        self._is_inverted = True
        self.name = self.name + '_INVERTED'

    def uninvert(self):
        """
        Uninverts the ground motion.
        Args:
            None
        Returns:
            None
        """
        if self.dt == -1.0:
            return  
        else:
            pass
        if self._is_inverted:
            self.gnd_acc *= -1
            self.gnd_vel *= -1
            self.gnd_disp *= -1
            self._is_inverted = False
            self.name = self.name.replace('_INVERTED', '')
        else:
            return
    
    def plot(self, acc: bool=True, vel: bool=True, disp: bool=True, enable: bool=True, called: bool=False):
        """
        Plots desired ground motion parameters.
        Args:
            acc (bool, optional): Plot acceleration.
            vel (bool, optional): Plot velocity.
            disp (bool, optional): Plot displacement.
            enable (bool, optional): Enable plotting of ground parameters. Used if called from a RigidBlock object.
            called (bool, optional): True if called from a RigidBlock object.
        Returns:
            fig, ax (plt.figure, plt.axis): Figure and axis objects if called from a RigidBlock object.
        """
        if self.dt == -1.0:
            return
        else:
            pass
        num_plots = sum([acc, vel, disp])
        remain_plots = num_plots
        if num_plots == 0:
            return
        elif num_plots == 1:
            fig, ax = plt.subplots(num=self.name)
            ax.set_xlabel('Time (s)')
        else:
            fig, ax = plt.subplots(num_plots, 1, num=self.name)
            ax[-1].set_xlabel('Time (s)')
        fig.suptitle('Ground Motion\n{}'.format(self.name))
        if enable:
            pass
        else:
            return fig, ax
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
            disp.set_ylabel('Displacement (m)')
            disp.set_title('Ground Displacement')
            disp.legend()
        if called:
            return fig, ax
        else:
            plt.show()