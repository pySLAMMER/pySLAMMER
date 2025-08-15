import warnings

import numpy as np
from numpy.typing import ArrayLike
from scipy.fft import rfft, rfftfreq

# TODO: bring this into utilities.py


class GroundMotion:
    """
    Ground Motion Record.

    Parameters
    ----------
    accel : np.ndarray or list
        Ground motion acceleration record in g.
    dt : float
        Time step of the record (s).
    name : str, optional
        Name of the record (default is 'None').

    Attributes
    ----------
    accel : np.ndarray
        Ground motion acceleration record in g.
    dt : float
        Time step of the record (s).
    name : str
        Name of the record.
    pga : float
        Peak ground acceleration in g.
    mean_period : float
        Mean period of the ground motion.
    """

    def __init__(self, accel: ArrayLike, dt: float, name: str = "None"):
        try:
            self.accel = np.array(accel, dtype=float)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Could not convert accel to numeric array: {e}")

        if self.accel.ndim != 1:
            raise ValueError(f"accel must be 1-dimensional, got {self.accel.ndim}D")

        # Validate dt range
        if dt > 0.1:
            warnings.warn(
                f"Time step dt={dt:.4f}s is unusually large for ground motion data. "
                f"Typical range is 0.001-0.04s. Please verify this is correct.",
                UserWarning,
                stacklevel=2,
            )
        elif dt <= 0:
            raise ValueError(f"Time step dt must be positive, got {dt}")

        self.dt = dt
        self.name = name
        self._npts = len(self.accel)
        self.pga = np.max(np.abs(self.accel))

        # Check for zero amplitude ground motion
        if self.pga == 0:
            warnings.warn(
                "This ground motion has zero amplitude",
                UserWarning,
                stacklevel=2,
            )
            self.mean_period = np.nan  # Set to NaN for zero amplitude
        else:
            # FFT
            x = rfft(accel)[1::]
            freqs = rfftfreq(self._npts, dt)[1::]
            x_real = np.real(x)
            x_imag = np.imag(x)
            c = np.sqrt(x_real**2 + x_imag**2)

            self.mean_period = sum(c**2 / freqs) / sum(c**2)

    def __str__(self):
        """
        String representation of the GroundMotion object.

        Returns
        -------
        str
            A string describing the ground motion record.
        """
        return (
            f"Ground Motion:\n"
            f"    Name: {self.name},\n"
            f"    PGA: {self.pga:.2f} g,\n"
            f"    dt: {self.dt:.3f} s,\n"
            f"    Duration: {self._npts * self.dt:.2f} s,\n"
            f"    Mean Period: {self.mean_period:.2f} s,\n"
            f"    npts: {self._npts}"
        )

    def __eq__(self, other):
        if not isinstance(other, GroundMotion):
            return NotImplemented
        return (
            np.array_equal(self.accel, other.accel)
            and self.dt == other.dt
            and self.name == other.name
        )
