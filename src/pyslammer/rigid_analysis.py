from typing import Optional

import numpy as np

from .constants import G_EARTH
from .ground_motion import GroundMotion
from .sliding_block_analysis import SlidingBlockAnalysis


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

    Raises
    ------
    ValueError
        If both `target_pga` and `scale_factor` are provided.

    Attributes
    ----------
    ground_acc : numpy.ndarray
        Ground acceleration time series (in m/s^2).
    """

    def __init__(
        self,
        ky: float,
        ground_motion: GroundMotion,
        scale_factor: float = 1.0,
        target_pga: Optional[float] = None,
    ) -> None:
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
        """
        super().__init__(ky, ground_motion, scale_factor, target_pga)

        self._npts = len(self.a_in)
        self.ground_acc = np.array(self.a_in) * G_EARTH
        self.dt = ground_motion.dt

        self.run_rigid_analysis()

    def __str__(self) -> str:
        return f"RigidAnalysis(ky={self.ky:.3f}g, max_disp={getattr(self, 'max_sliding_disp', 0):.3f}m)"

    def __repr__(self) -> str:
        return f"RigidAnalysis(ky={self.ky}, ground_motion={self.ground_motion!r}, scale_factor={getattr(self, 'scale_factor', 1.0)}, target_pga={getattr(self, 'target_pga', None)})"

    def run_rigid_analysis(self):
        """
        Calculate the downslope rigid block displacement, differential velocity, and acceleration.

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
