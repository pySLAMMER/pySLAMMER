import numpy as np
import scipy.integrate as spint

from .decoupled_analysis import assign_k_y
from .sliding_block_analysis import SlidingBlockAnalysis

M_TO_CM = 100
G_EARTH = 9.80665  # Acceleration due to gravity (m/block_disp^2).


class RigidAnalysis(SlidingBlockAnalysis):
    """
    Rigid Block Analysis.

    Parameters
    ----------
    ky : float
        Critical acceleration (in g).
    ground_motion : GroundMotion
        Ground motion object containing acceleration time history and time step.
    scale_factor : float, optional
        Scaling factor for the input acceleration. Default is 1.0.
    target_pga : float, optional
        Target peak ground acceleration (in m/s^2). If provided, the input acceleration
        will be scaled to match this value. Cannot be used with `scale_factor`.
    method : str, optional
        Analysis method. Options are 'jibson', 'dgr', or 'gra'. Default is 'jibson'.

    Raises
    ------
    ValueError
        If both `target_pga` and `scale_factor` are provided.

    Attributes
    ----------
    analysis_methods : dict
        Dictionary mapping method names to their corresponding functions.
    ground_acc : numpy.ndarray
        Ground acceleration time series (in m/s^2).
    """

    def __init__(
        self, ky, ground_motion, scale_factor=1.0, target_pga=None, method="jibson"
    ):
        """
        Initialize rigid block analysis.

        Parameters
        ----------
        ky : float
            Critical acceleration (in g).
        ground_motion : GroundMotion
            Ground motion object containing acceleration time series and metadata.
        scale_factor : float, optional
            Scaling factor for the input acceleration. Default is 1.0.
        target_pga : float, optional
            Target peak ground acceleration (in m/s^2). If provided, the input acceleration
            will be scaled to match this value. Cannot be used with `scale_factor`.
        method : str, optional
            Analysis method. Options are 'jibson', 'dgr', or 'gra'. Default is 'jibson'.
        """
        super().__init__(ky, ground_motion, scale_factor, target_pga)

        self.analysis_methods = {
            "jibson": self.jibson,
            "dgr": self._downslope_dgr,
            "gra": self._garcia_rivas_arnold,
        }
        self._npts = len(self.a_in)
        self.ground_acc = np.array(self.a_in) * G_EARTH
        self.dt = ground_motion.dt
        # self.ky = ky * G_EARTH
        self.method = method

        analysis_function = self.analysis_methods.get(self.method)
        if analysis_function:
            analysis_function()
        else:
            raise ValueError(f"Unknown method: {self.method}")

    def __str__(self):
        # if self.dt == -1.0:
        #     info = ('Record: {}\n'.format(self.name))
        # else:
        #     info = (
        #             'Rigid Block Analysis\n'
        #             +'Record  : {}\n'.format(self.name)
        #             +'PGA     : {:.3f} g\n'.format(self.pga)
        #             +'dt      : {:.3f} s\n'.format(self.dt)
        #             +'ky     : {:.3f} m/s^2\n'.format(self.ky)
        #             +'Disp    : {:.3f} m'.format(self.total_disp)
        #         )
        # return info
        # TODO: Re-implement
        return "Rigid Block Analysis"

    def jibson(self):
        """
        Calculate the downslope rigid block displacement, differential velocity, and acceleration using the Jibson method.

        Notes
        -----
        This method iteratively calculates the block's acceleration, velocity, and displacement
        based on the input ground acceleration and critical acceleration.
        """
        tol = 1e-5
        self.block_acc = np.zeros(len(self.ground_acc))
        self.sliding_vel = np.zeros(len(self.ground_acc))
        self.sliding_disp = np.zeros(len(self.ground_acc))
        # [previous, current]
        acc = [0, 0]
        vel = [0, 0]
        pos = [0, 0]

        for i in range(len(self.ground_acc)):
            gnd_acc_curr = self.ground_acc[i]
            if vel[1] < tol:
                if abs(gnd_acc_curr) > self.ky:
                    n = gnd_acc_curr / abs(gnd_acc_curr)
                else:
                    n = gnd_acc_curr / self.ky
            else:
                n = 1
            acc[1] = gnd_acc_curr - n * self.ky
            vel[1] = vel[0] + (self.dt / 2) * (acc[1] + acc[0])
            if vel[1] > 0:
                pos[1] = pos[0] + (self.dt / 2) * (vel[1] + vel[0])
            else:
                vel[1] = 0
                acc[1] = 0
            pos[0] = pos[1]
            vel[0] = vel[1]
            acc[0] = acc[1]
            self.sliding_disp[i] = pos[1]
            self.sliding_vel[i] = vel[1]
            self.block_acc[i] = gnd_acc_curr - acc[1]
        self.max_sliding_disp = self.sliding_disp[-1]

    def _garcia_rivas_arnold(self):
        """
        Placeholder for future implementation using the velocity Verlet method.

        Notes
        -----
        This method is not yet implemented.
        """
        pass

    def _downslope_dgr(self):
        """
        Calculate the downslope rigid block displacement, differential velocity, and acceleration using the DGR method.

        Notes
        -----
        This method is a placeholder for future implementation.
        """
        if self.dt == -1.0:
            return
        else:
            self._clear_block_params()
            self.ky = assign_k_y(ky) * G_EARTH
        time = np.arange(0, len(self.ground_acc) * self.dt, self.dt)
        block_sliding = False
        for i in range(len(self.gnd_acc)):
            if i == 0:
                self.block_acc.append(self.gnd_acc[i])
                self.block_vel.append(self.gnd_vel[i])
                continue
            tmp_block_vel = self.block_vel[i - 1] + self.ky * self.dt
            if self.gnd_acc[i] > self.ky:
                block_sliding = True
            elif tmp_block_vel > self.gnd_vel[i]:
                block_sliding = False
            else:
                pass
            if block_sliding:
                self.block_vel.append(tmp_block_vel)
                self.block_acc.append(self.ky)
            else:
                self.block_acc.append(self.gnd_acc[i])
                self.block_vel.append(self.gnd_vel[i])
        self.block_vel = abs(self.gnd_vel - self.block_vel)
        self.block_disp = spint.cumulative_trapezoid(self.block_vel, time, initial=0)
        self.total_disp = self.block_disp[-1]
