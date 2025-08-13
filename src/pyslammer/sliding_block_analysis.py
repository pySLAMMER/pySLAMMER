import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate as spint

from pyslammer.constants import G_EARTH
from pyslammer.utilities import psfigstyle


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
    ground_motion : GroundMotion
        Ground motion object containing acceleration time series and metadata.
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
        Yield acceleration of the sliding block (in g).
    time : numpy.ndarray or None
        Time array corresponding to the input acceleration.
    ground_acc : numpy.ndarray or None
        Ground acceleration time series (in m/s^2).
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

    def __init__(self, ky, ground_motion, scale_factor=1.0, target_pga=None):
        if target_pga is not None:
            if scale_factor != 1:
                raise ValueError(
                    "Both target_pga and scale_factor cannot be provided at the same time."
                )
            scale_factor = target_pga / max(abs(ground_motion.accel))

        self.scale_factor = scale_factor
        self.a_in = (
            ground_motion.accel.copy() * scale_factor
        )  # no longer accepts lists, only numpy arrays
        self.dt = ground_motion.dt

        self.method = None
        self.motion_name = ground_motion.name
        self.ky = ky * G_EARTH
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

    def _compile_attributes(self):
        time = np.arange(0, self._npts * self.dt, self.dt)
        if self.ground_vel is None:
            self.ground_vel = spint.cumulative_trapezoid(
                self.ground_acc, time, initial=0
            )
            self.ground_disp = spint.cumulative_trapezoid(
                self.ground_vel, time, initial=0
            )
        if self.sliding_vel is None:
            self.sliding_vel = self.ground_vel - self.block_vel
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
        self._compile_attributes()
        bclr = "k"
        gclr = "tab:blue"
        inp_clr = "tab:gray"
        kyclr = "k"
        if fig is None:  # gAcc,gVel,bVel,bDisp,t,ky):
            fig, axs = plt.subplots(3, 1, sharex=True)
        else:
            axs = fig.get_axes()
        time = np.arange(0, self._npts * self.dt, self.dt)

        # Add analysis summary text above the plots
        analysis_type = self.__class__.__name__
        motion_name = getattr(self, "motion_name", "Unknown")
        summary_text = f"{analysis_type} | ky: {self.ky / G_EARTH:.2f}g | Motion: {motion_name} (PGA: {max(abs(self.a_in)):.2f}g)"
        fig.suptitle(summary_text, fontsize=10, y=0.98)

        if hasattr(self, "HEA") and self.HEA is not None:
            axs[0].plot(
                time, self.ground_acc / G_EARTH, label="Input Acc.", color=inp_clr
            )
            axs[0].plot(
                time,
                self.HEA / G_EARTH,
                label="Base Acc.",
                color=gclr,
            )
        else:
            axs[0].plot(time, self.ground_acc / G_EARTH, label="Base Acc.", color=gclr)

        axs[0].plot(time, self.block_acc / G_EARTH, label="Block Acc.", color=bclr)

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
        fig.canvas.toolbar_position = "top"
        return fig


if __name__ == "__main__":
    from pyslammer.rigid_analysis import RigidAnalysis
    from pyslammer.utilities import sample_ground_motions

    record_name = "Kobe_1995_TAK-090"
    gm = sample_ground_motions()[record_name]
    rigid_inputs = {"ground_motion": gm, "ky": 0.2}

    rigid_result = RigidAnalysis(**rigid_inputs, scale_factor=2)
    plt.close("all")
    fig = rigid_result.sliding_block_plot(time_range=[2, 10])
    plt.show()
