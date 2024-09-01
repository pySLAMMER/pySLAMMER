import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as spint

G_EARTH = 9.80665 # Acceleration due to gravity (m/s^2).


class Record():
    """Ground Motion Record."""

    def __init__(self, gnd_motion: np.ndarray=[], name: str='None'):
        """
        Creates a ground motion record object.
        Args:
            gnd_motion (np.ndarray): Ground motion record.
            name (str): Name of the record.
        """
        if len(gnd_motion) == 0:
            self.name = 'Empty Record'
            self.dt = -1.0
            self.pga = 0.0
        else:
            self._gnd_motion = np.array(gnd_motion)
            self._is_scaled = False
            self._is_inverted = False
            self.name = name            
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
        # Assigns and calculates ground motion parameters.
        self.gnd_acc = self._gnd_motion[1][:] * G_EARTH
        self.gnd_vel = spint.cumulative_trapezoid(self.gnd_acc, self.time, initial=0)
        self.gnd_disp = spint.cumulative_trapezoid(self.gnd_vel, self.time, initial=0)
        self.pga = max(abs(self.gnd_acc)) / G_EARTH
    
    def scale(self, pga: float=False, scale_factor: float=False):
        """
        Scale the ground motion using desired method. Does nothing if more than one method is selected.
        Args:
            pga (float, optional): Desired peak ground acceleration in g.
            scale_factor (float, optional): Desired scale factor.
        Returns: 
            None
        """
        check_list = [pga, scale_factor]
        if sum(check_list) != 1:
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
        if self._is_inverted:
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
        if self._is_inverted:
            self.gnd_acc *= -1
            self.gnd_vel *= -1
            self.gnd_disp *= -1
            self._is_inverted = False
            self.name = self.name.replace('_INVERTED', '')
        else:
            return
    
    def plot(self, acc: bool=True, vel: bool=True, disp: bool=True, enable: bool=True):
        """
        Plots desired ground motion parameters.
        Args:
            acc (bool, optional): Plot acceleration.
            vel (bool, optional): Plot velocity.
            disp (bool, optional): Plot displacement.
            enable (bool, optional): Enable plotting of ground parameters. Used if called from a RigidBlock object.
        Returns:
            fig, ax (plt.figure, plt.axis): Figure and axis objects.
        """
        if self.dt == -1.0:
            return
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
        plt.show()
        return fig, ax