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
    _ground_acc_ : numpy.ndarray
        Internal ground acceleration time series (in m/s^2).
    ky : float
        Yield acceleration (in g) for user interface.
    _ky_ : float
        Internal yield acceleration (in m/s^2) for calculations.
    """

    def __init__(
        self,
        ky: float,
        ground_motion: GroundMotion,
        scale_factor: float = 1.0,
        target_pga: Optional[float] = None,
        inverse: bool = False,
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
        inverse : bool, optional
            If True, inverts the direction of the ground motion by negating the scale factor.
            Default is False.
        """
        super().__init__(ky, ground_motion, scale_factor, target_pga, inverse)

        self._ground_acc_ = (
            np.array(self.a_in) * G_EARTH
        )  # Internal ground acceleration in m/s²
        # dt is already set by parent class

        self.run_rigid_analysis()

    def __str__(self):
        return (
            f"RigidAnalysis:\n"
            f"  ky: {self.ky} g,\n"
            f"  {self.ground_motion},\n"
            f"  Scale factor: {self.scale_factor},\n"
            f"  Displacement: {100 * getattr(self, 'max_sliding_disp', 0):.1f} cm"
        )

    def __eq__(self, other):
        if not isinstance(other, RigidAnalysis):
            return NotImplemented
        return super().__eq__(other)

    def run_rigid_analysis(self):
        """
        Calculate the downslope rigid block displacement, differential velocity, and acceleration.

        Notes
        -----
        This method iteratively calculates the block's acceleration, velocity, and displacement
        based on the input ground acceleration and critical acceleration.
        """
        tol = 1e-5
        self._block_acc_ = np.zeros(len(self._ground_acc_))
        self.sliding_vel = np.zeros(len(self._ground_acc_))
        self.sliding_disp = np.zeros(len(self._ground_acc_))
        # [previous, current]
        acc = [0, 0]
        vel = [0, 0]
        pos = [0, 0]

        for i in range(len(self._ground_acc_)):
            gnd_acc_curr = self._ground_acc_[i]
            if vel[1] < tol:
                if abs(gnd_acc_curr) > self._ky_:
                    n = gnd_acc_curr / abs(gnd_acc_curr)
                else:
                    n = gnd_acc_curr / self._ky_
            else:
                n = 1
            acc[1] = gnd_acc_curr - n * self._ky_
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
            self._block_acc_[i] = gnd_acc_curr - acc[1]
        self.max_sliding_disp = self.sliding_disp[-1]
