from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate as spint

from .constants import G_EARTH
from .ground_motion import GroundMotion
from .utilities import psfigstyle


class SlidingBlockAnalysis:
    """
    Base class for all time-domain sliding block analyses. `SlidingBlockAnalysis` does not
    perform any analysis by itself. It is meant to be subclassed by other classes that
    implement specific sliding block analysis methods.
    It performs checks on the input parameters and initializes the attributes for the analysis.
    The class also provides a method to plot the results of the analysis.

    Parameters
    ----------
    ky : float
        Yield acceleration of the sliding block (in g).
    ground_motion : GroundMotion or dict
        Ground motion data. Can be:
        - A GroundMotion object
        - A dictionary with keys: 'accel', 'dt', and optionally 'name'
          Example: {'accel': [0.1, 0.2, 0.1], 'dt': 0.01, 'name': 'MyMotion'}
    scale_factor : float, optional
        Scaling factor for the input acceleration. Default is 1.0.
    target_pga : float, optional
        Target peak ground acceleration (in g). If provided, the input acceleration
        will be scaled to match this value. Cannot be used with `scale_factor`.

    Raises
    ------
    ValueError
        If both `target_pga` and `scale_factor` are provided.

    Attributes
    ----------
    scale_factor : float
        Scaling factor applied to the input acceleration.
    a_in : numpy.ndarray
        Scaled input acceleration time series.
    dt : float
        Time step of the input acceleration time series (in seconds).
    motion_name : str
        Name of the ground motion record.
    method : str or None
        Analysis method used (to be defined in subclasses).
    ky : float or None
        Yield acceleration of the sliding block (in g) for user interface.
    _ky_ : float or None
        Internal yield acceleration (in m/s^2) for calculations.
    time : numpy.ndarray or None
        Time array corresponding to the input acceleration.
    _ground_acc_ : numpy.ndarray or None
        Internal ground acceleration time series (in m/s^2).
    ground_vel : numpy.ndarray or None
        Ground velocity time series (in m/s).
    ground_disp : numpy.ndarray or None
        Ground displacement time series (in m).
    block_acc : numpy.ndarray or None
        Block acceleration time series (in m/s^2).
    block_vel : numpy.ndarray or None
        Block velocity time series (in m/s).
    block_disp : numpy.ndarray or None
        Block displacement time series (in m).
    sliding_vel : numpy.ndarray or None
        Sliding velocity time series (in m/s).
    sliding_disp : numpy.ndarray or None
        Sliding displacement time series (in m).
    max_sliding_disp : float or None
        Maximum sliding displacement (in m).
    _npts : int or None
        Number of points in the input acceleration time series.
    """

    def __init__(
        self,
        ky,
        ground_motion: Union[GroundMotion, dict],
        scale_factor=1.0,
        target_pga=None,
    ):
        # Convert dict to GroundMotion if needed
        if isinstance(ground_motion, dict):
            try:
                ground_motion = self._dict_to_ground_motion(ground_motion)
            except (KeyError, TypeError, ValueError) as e:
                raise ValueError(f"Invalid ground_motion dictionary: {e}")
        elif not isinstance(ground_motion, GroundMotion):
            raise TypeError(
                f"ground_motion must be GroundMotion object or dict, got {type(ground_motion)}"
            )

        # Validate ky
        if ky <= 0:
            raise ValueError(
                f"Yield acceleration ky must be positive, got {ky} (upslope sliding not yet supported)."
            )

        if target_pga is not None:
            if scale_factor != 1:
                raise ValueError(
                    "Both target_pga and scale_factor cannot be provided at the same time."
                )
            scale_factor = target_pga / max(abs(ground_motion.accel))

        self.ground_motion = ground_motion
        self.scale_factor = scale_factor
        self.a_in = ground_motion.accel.copy() * scale_factor
        self._npts = ground_motion._npts
        self.dt = ground_motion.dt
        self.motion_name = ground_motion.name
        self.method = None
        self.ky = ky  # Keep original value in g for user interface
        self._ky_ = ky * G_EARTH  # Internal value in m/s² for calculations
        self.time = None

        self._ground_acc_ = None  # Internal ground acceleration in m/s²
        self.ground_vel = None
        self.ground_disp = None

        self._block_acc_ = None
        self.block_vel = None
        self.block_disp = None

        self.sliding_vel = None
        self.sliding_disp = None
        self.max_sliding_disp = None
        pass

    def __str__(self):
        return (
            f"SlidingBlockAnalysis:\n"
            f"  ky: {self.ky} g,\n"
            f"  {self.ground_motion},\n"
            f"  Scale factor: {self.scale_factor}."
        )

    def __eq__(self, other):
        if not isinstance(other, SlidingBlockAnalysis):
            return NotImplemented
        return (
            self.ky == other.ky
            and self._ky_ == other._ky_
            and np.array_equal(self.a_in, other.a_in)
            and self.dt == other.dt
            and self.motion_name == other.motion_name
            and self.scale_factor == other.scale_factor
        )

    @staticmethod
    def _dict_to_ground_motion(gm_dict: dict) -> GroundMotion:
        """
        Convert a dictionary to a GroundMotion object.

        Parameters
        ----------
        gm_dict : dict
            Dictionary with required keys 'accel' and 'dt', optional 'name'

        Returns
        -------
        GroundMotion
            Constructed GroundMotion object

        Raises
        ------
        KeyError
            If required keys are missing
        TypeError
            If invalid parameters are passed to GroundMotion
        """
        required_keys = {"accel", "dt"}
        if not required_keys.issubset(gm_dict.keys()):
            missing = required_keys - gm_dict.keys()
            raise KeyError(f"Missing required keys: {missing}")

        return GroundMotion(**gm_dict)

    @staticmethod
    def _motion_integration(motion: np.ndarray, dt: float) -> np.ndarray:
        """
        Integrate a component of motion (acceleration or velocity) to get its
        integral (velocity or displacement).

        Parameters
        ----------
        motion : numpy.ndarray
            The input motion time series (acceleration or velocity).
            The input units for acceleration should not be in terms of g.
        dt : float
            The time step of the motion time series (in seconds).

        Returns
        -------
        numpy.ndarray
            The integrated motion time series (velocity or displacement).
        """
        return spint.cumulative_trapezoid(motion, dx=dt, initial=0)

    def _compile_base_attributes(self):
        if self._ground_acc_ is None:
            self._ground_acc_ = self.a_in * G_EARTH
        if self.ground_vel is None:
            self.ground_vel = self._motion_integration(self._ground_acc_, self.dt)
        if self.ground_disp is None:
            self.ground_disp = self._motion_integration(self.ground_vel, self.dt)
        pass

    def _compile_block_attributes(self):
        if self.block_vel is None:
            self.block_vel = self._motion_integration(self._block_acc_, self.dt)  # type: ignore[operator]
        if self.block_disp is None:
            self.block_disp = self._motion_integration(self.block_vel, self.dt)
        pass

    def _compile_sliding_attributes(self):
        self._compile_base_attributes()
        self._compile_block_attributes()
        if self.sliding_vel is None:
            self.sliding_vel = self.ground_vel - self.block_vel  # type: ignore[operator]
        if self.sliding_disp is None:
            self.sliding_disp = self.block_disp  # - self.ground_disp
        pass

    def sliding_block_plot(self, time_range=None, sliding_vel_mode=True, fig=None):
        """
        Plot the analysis result as a 3-by-1 array of time series figures.

        Parameters
        ----------
        sliding_vel_mode : bool, optional
            If True, the velocity figure shows the sliding (relative) velocity of the block.
            If False, it shows the absolute velocities of the input motion and the block.
            Default is True.
        fig : matplotlib.figure.Figure, optional
            Existing figure to plot on. If None, a new figure is created. Default is None.

        Returns
        -------
        matplotlib.figure.Figure
            The figure containing the plots.
        """
        plt.style.use(psfigstyle)
        self._compile_sliding_attributes()
        bclr = "k"
        gclr = "tab:blue"
        inp_clr = "tab:gray"
        if fig is None:  # gAcc,gVel,bVel,bDisp,t,ky):
            fig, axs = plt.subplots(3, 1, sharex=True)
        else:
            axs = fig.get_axes()
        time = np.arange(0, self._npts * self.dt, self.dt)  # type: ignore[operator]

        # Add analysis summary text above the plots
        analysis_type = self.__class__.__name__
        motion_name = getattr(self, "motion_name", "Unknown")
        summary_text = f"{analysis_type} | ky: {self.ky:.2f}g | Motion: {motion_name} (PGA: {max(abs(self.a_in)):.2f}g)"
        fig.suptitle(summary_text, fontsize=10, y=0.98)

        if hasattr(self, "HEA") and self.HEA is not None:  # type: ignore[attr-defined]
            axs[0].plot(
                time,
                self._ground_acc_ / G_EARTH,  # type: ignore[operator]
                label="Input Acc.",
                color=inp_clr,  # type: ignore[operator]
            )
            axs[0].plot(
                time,
                self.HEA / G_EARTH,  # type: ignore[attr-defined]
                label="Base Acc.",
                color=gclr,
            )
        else:
            axs[0].plot(
                time,
                self._ground_acc_ / G_EARTH,  # type: ignore
                label="Base Acc.",
                color=gclr,
            )

        axs[0].plot(time, self._block_acc_ / G_EARTH, label="Block Acc.", color=bclr)  # type: ignore[operator]

        axs[0].set_ylabel("Acc. (g)")
        axs[0].set_xlim([time[0], time[-1]])

        if sliding_vel_mode:
            axs[1].plot(time, self.sliding_vel, label="Sliding Vel.", color=bclr)
        else:
            axs[1].plot(time, self.ground_vel, label="Base Vel.", color=gclr)
            axs[1].plot(time, self.block_vel, label="Block Vel.", color=bclr)
        axs[1].set_ylabel("Vel. (m/s)")

        axs[2].plot(time, self.sliding_disp, label="Sliding Disp.", color=bclr)
        axs[2].set_ylabel("Disp. (m)")
        for i in range(len(axs)):
            axs[i].grid(which="both")
            # Position legends inside the axis limits
            if i == 0 or i == 1:  # Acc and Vel plots
                axs[i].legend(loc="upper right")
            else:  # Disp plot
                axs[i].legend(loc="lower right")
        # Only the bottom plot (Disp) should show the xlabel
        axs[2].set_xlabel("Time (s)")

        if time_range is not None:
            if (
                not isinstance(time_range, (list, tuple))
                or len(time_range) != 2
                or not all(isinstance(val, (int, float)) for val in time_range)
                or time_range[0] >= time_range[1]
                or time_range[0] < time[0]
                or time_range[1] > time[-1]
            ):
                raise ValueError(
                    "`time_range` must be a list or tuple with two numeric values within the time range, and the second value must be larger than the first."
                )
            axs[0].set_xlim(time_range)
            axs[1].set_xlim(time_range)
            axs[2].set_xlim(time_range)

        fig.tight_layout()
        return fig
