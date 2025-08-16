# Decoupled Block Analysis
# TODO: add docstrings
# TODO: add inherited variable values
# TODO: add "testing" features?
import math

import matplotlib.pyplot as plt
import numpy as np

from .constants import G_EARTH, KNM3_TO_LBFT3, M_TO_FT
from .ground_motion import GroundMotion
from .sliding_block_analysis import SlidingBlockAnalysis
from .utilities import sample_ground_motions


def mod_damp_testing(effective_strain, ref_strain):
    g_over_gmax = strain_mod_update(effective_strain, ref_strain)
    new_damp = strain_damp_update(g_over_gmax, effective_strain, ref_strain)
    return g_over_gmax, new_damp


def strain_mod_update(effective_strain, ref_strain):
    return 1 / (
        1 + (effective_strain / ref_strain) ** 1
    )  # TODO: move constants outside of function


def strain_damp_update(g_over_gmax, shear_strain, ref_strain):
    m1 = 1 / math.pi
    m2 = shear_strain
    m3 = ref_strain
    m4 = shear_strain + ref_strain
    m5 = m4 / m3
    m6 = m2**2 / m4
    masing_damping = m1 * (4 * (m2 - m3 * math.log(m5)) / m6 - 2)

    new_damp = (
        0.62 * g_over_gmax**0.1 * masing_damping + 0.01
    )  # TODO: move constants outside of function

    if equivalent_linear_testing:
        print(f"g_over_gmax: {g_over_gmax}")
        print(f"masing_damping: {masing_damping}")
        print(f"new_damp: {new_damp}")

    return new_damp


def impedance_damping(vs_base, vs_slope):
    # Adjust for base impedance. include_impedance_damping()?
    vs_ratio = vs_base / vs_slope
    damp_imp = 0.55016 * vs_ratio**-0.9904  # TODO: move constants outside of function
    damp_imp = min(damp_imp, 0.2)  # TODO: move constants outside of function
    return damp_imp


def constant_k_y(k_y):
    def _ky_func(disp):
        return k_y

    return _ky_func


def interpolated_k_y(k_y):
    def _ky_func(disp):
        disp_values, ky_values = k_y
        return np.interp(disp, disp_values, ky_values)

    if k_y_testing:
        for disp in [0, 10, 20, 30, 40, 50]:
            print(f"disp: {disp}, ky: {_ky_func(disp)}")
    return _ky_func


def assign_k_y(k_y):
    if isinstance(k_y, float):
        return constant_k_y(k_y)
    elif isinstance(k_y, tuple) and len(k_y) == 2:
        return interpolated_k_y(k_y)
    elif callable(k_y):
        return k_y
    else:
        val_error_msg = (
            "Invalid type for ky. Must be float, tuple, or callable."
            "If tuple, must contain two equal-length lists or numpy arrays."
        )
        raise ValueError(val_error_msg)


# FIXME: inconsistent use of a_in with/without scale_factor
class Decoupled(SlidingBlockAnalysis):
    """
    Decoupled analysis for sliding block and ground motion interaction.

    Parameters
    ----------
    ky : float or tuple[list[float], list[float]] or tuple[np.ndarray, np.ndarray] or callable
        Yield acceleration function or constant.
    ground_motion : GroundMotion
        Ground motion object containing acceleration time history and time step.
    height : int or float
        Height of the sliding block.
    vs_slope : int or float
        Shear wave velocity of the slope.
    vs_base : int or float
        Shear wave velocity of the base.
    damp_ratio : float
        Damping ratio of the sliding block.
    ref_strain : float
        Reference strain for modulus reduction.
    scale_factor : float, optional
        Scale factor for the input acceleration. Default is 1.
    soil_model : str, optional
        Soil model type. Default is "linear_elastic".
    si_units : bool, optional
        Whether to use SI units. Default is True.
    lite : bool, optional
        Whether to use lite mode. Default is False.

    Attributes
    ----------
    k_y : callable
        Yield acceleration function.
    a_in : list[float] or np.ndarray
        Input acceleration time history.
    dt : float
        Time step of the input acceleration.
    height : int or float
        Height of the sliding block.
    vs_slope : int or float
        Shear wave velocity of the slope.
    vs_base : int or float
        Shear wave velocity of the base.
    damp_ratio : float
        Damping ratio of the sliding block.
    ref_strain : float
        Reference strain for modulus reduction.
    scale_factor : float
        Scale factor for the input acceleration.
    soil_model : str
        Soil model type.
    si_units : bool
        Whether to use SI units.
    lite : bool
        Whether to use lite mode.
    npts : int
        Number of points in the input acceleration time history.
    g : float
        Gravitational acceleration.
    unit_weight : float
        Unit weight of the sliding block.
    rho : float
        Density of the sliding block.
    mass : float
        Mass of the sliding block.
    max_shear_mod : float
        Maximum shear modulus of the sliding block.
    HEA : np.ndarray
        Horizontal earthquake acceleration.
    block_disp : np.ndarray
        Displacement of the sliding block.
    block_vel : np.ndarray
        Velocity of the sliding block.
    block_acc : np.ndarray
        Acceleration of the sliding block.
    x_resp : np.ndarray
        Response displacement.
    v_resp : np.ndarray
        Response velocity.
    a_resp : np.ndarray
        Response acceleration.
    max_sliding_disp : float
        Maximum sliding displacement.
    ground_acc : np.ndarray
        Ground acceleration.
    """

    def __init__(
        self,
        ky: float
        or tuple[list[float], list[float]]
        or tuple[np.ndarray, np.ndarray]
        or callable,
        ground_motion: GroundMotion,
        height: int or float,
        vs_slope: int or float,
        vs_base: int or float,
        damp_ratio: float,
        ref_strain: float,
        scale_factor: float = 1,
        target_pga: float = None,
        soil_model: str = "linear_elastic",
        si_units: bool = True,
        lite: bool = False,
        inverse: bool = False,
    ):
        super().__init__(ky, ground_motion, scale_factor, target_pga, inverse)
        self._npts = len(self.a_in)
        self.k_y = assign_k_y(ky)
        self.dt = ground_motion.dt
        self.height = height
        self.vs_slope = vs_slope
        self.vs_base = vs_base
        self.damp_ratio = damp_ratio
        self.ref_strain = ref_strain
        self.SI_units = si_units
        self.soil_model = soil_model
        self.lite = lite

        self.npts = len(self.a_in)
        self.g = G_EARTH * (si_units + (not si_units) * M_TO_FT)
        self.unit_weight = 20.0 * (
            si_units + (not si_units) * KNM3_TO_LBFT3
        )  # TODO: move constants outside of function
        self.rho = self.unit_weight / self.g  # DENSITY
        self.mass = self.unit_weight * height / self.g
        self.L1 = -2.0 * self.mass / math.pi * math.cos(math.pi)
        self.M1 = self.mass / 2.0
        self.max_shear_mod = self.rho * vs_slope**2

        self.HEA = np.zeros(self.npts)
        self.sliding_vel = np.zeros(self.npts)
        self.block_disp = np.zeros(self.npts)
        self.block_vel = np.zeros(self.npts)
        self._block_acc_ = np.zeros(self.npts)
        self.x_resp = np.zeros(self.npts)
        self.v_resp = np.zeros(self.npts)
        self.a_resp = np.zeros(self.npts)
        self.max_sliding_disp = 0.0

        # special variables that change during the analysis
        self._slide = False
        self._vs_slope = vs_slope
        self._omega = math.pi * vs_slope / (2.0 * height)
        self._damp_imp = impedance_damping(vs_base, vs_slope)
        self._damp_tot = damp_ratio + self._damp_imp

        if type(self) is Decoupled:
            self.run_sliding_analysis()
        self._ground_acc_ = self.a_in * self.g

    def __str__(self):
        return (
            f"Decoupled:\n"
            f"  ky: {self.ky} g,\n"
            f"  {self.ground_motion},\n"
            f"  Scale factor: {self.scale_factor},\n"
            f"  Displacement: {100 * getattr(self, 'max_sliding_disp', 0):.1f} cm"
        )

    def __eq__(self, other):
        if not isinstance(other, Decoupled):
            return NotImplemented
        return super().__eq__(other)

    def run_sliding_analysis(self):  # TODO: add ca to inputs
        if self.soil_model == "equivalent_linear":
            self.equivalent_linear()

        for i in range(1, self.npts + 1):
            self.dynamic_response(i)

        # calculate decoupled displacements
        for i in range(1, self.npts + 1):
            self.sliding(i)

        self.max_sliding_disp = self.block_disp[-1]
        return self.max_sliding_disp

    def sliding(self, i):  # TODO: refactor
        # variables for the previous and current time steps
        # prev and curr are equal for the first time step
        # TODO: consider just starting at i=2 and eliminating the logical statement in prev
        # alternatively, removing logical and letting it use the last value of the array...
        prev = i - 2 + (i == 1)
        curr = i - 1

        yield_acc = self.k_y(self.block_disp[prev]) * self.g
        excess_acc = yield_acc - self.HEA[prev]
        delta_hea = self.HEA[curr] - self.HEA[prev]

        if k_y_testing:
            if i % 500 == 0:
                print(
                    f"disp: {self.block_disp[prev]}, ky: {self.k_y(self.block_disp[prev])}"
                )

        if not self._slide:
            self._block_acc_[curr] = self.HEA[curr]
            self.block_vel[curr] = 0
            self.block_disp[curr] = self.block_disp[prev]
            if self.HEA[curr] > yield_acc:
                self._slide = True
        else:
            self._block_acc_[curr] = yield_acc
            self.block_vel[curr] = (
                self.block_vel[prev] + (excess_acc - 0.5 * delta_hea) * self.dt
            )
            self.block_disp[curr] = (
                self.block_disp[prev]
                - self.block_vel[prev] * self.dt
                - 0.5 * (excess_acc + delta_hea / 6.0) * self.dt**2
            )
            if self.block_vel[curr] >= 0.0:
                self._slide = False
        self.sliding_vel[curr] = -self.block_vel[prev]

    def dynamic_response(self, i):
        prev = i - 2 + (i == 1)
        curr = i - 1
        # Newmark Beta Method constants
        beta = 0.25  # TODO: move outside of function (up to delta_a_in)
        gamma = 0.5  # TODO: move constants outside of function

        self._omega = (
            math.pi * self._vs_slope / (2.0 * self.height)
        )  # TODO: move outside of function

        k_eff = (
            self._omega**2
            + 2.0 * self._damp_tot * self._omega * gamma / (beta * self.dt)
            + 1.0 / (beta * self.dt**2)
        )
        a = 1.0 / (beta * self.dt) + 2.0 * self._damp_tot * self._omega * gamma / beta
        b = 1.0 / (2.0 * beta) + 2.0 * self.dt * self._damp_tot * self._omega * (
            gamma / (2.0 * beta) - 1.0
        )

        delta_a_in = self.a_in[curr] - self.a_in[prev]
        delta_force = (
            -self.L1 / self.M1 * delta_a_in * self.g * self.scale_factor
            + a * self.v_resp[prev]
            + b * self.a_resp[prev]
        )
        delta_x_resp = delta_force / k_eff
        delta_v_resp = (
            gamma / (beta * self.dt) * delta_x_resp
            - gamma / beta * self.v_resp[prev]
            + self.dt * (1.0 - gamma / (2.0 * beta)) * self.a_resp[prev]
        )
        delta_a_resp = (
            1.0 / (beta * (self.dt * self.dt)) * delta_x_resp
            - 1.0 / (beta * self.dt) * self.v_resp[prev]
            - 0.5 / beta * self.a_resp[prev]
        )

        self.x_resp[curr] = self.x_resp[prev] + delta_x_resp
        self.v_resp[curr] = self.v_resp[prev] + delta_v_resp
        self.a_resp[curr] = self.a_resp[prev] + delta_a_resp

        self.HEA[curr] = (
            self.a_in[curr] * self.g + self.L1 / self.mass * self.a_resp[curr]
        )

    def equivalent_linear(self):
        tol = 0.05  # TODO: move constants outside of function
        max_iterations = 100  # TODO: move constants outside of function
        rel_delta_mod = 1
        rel_delta_damp = 1
        shear_mod = self.max_shear_mod
        damp_ratio = self.damp_ratio
        count = 0
        while (
            rel_delta_damp > tol or rel_delta_mod > tol
        ):  # TODO: confirm whether number of iterations and order of operations matches SLAMMER
            for i in range(1, self.npts + 1):
                self.dynamic_response(i)
            peak_disp = max(abs(self.x_resp))
            effective_strain = (
                0.65 * 1.57 * peak_disp / self.height
            )  # TODO: move constants outside of function
            g_over_gmax = strain_mod_update(effective_strain, self.ref_strain)
            new_mod = g_over_gmax * self.max_shear_mod
            new_damp = strain_damp_update(
                g_over_gmax, effective_strain, self.ref_strain
            )

            if equivalent_linear_testing:
                print(f"iteration: {count}")
                print(f"effective_strain: {effective_strain}")
                print(f"_vs_slope: {self._vs_slope}")
                print(f"_damp_tot: {self._damp_tot}")

            self._vs_slope = math.sqrt(new_mod / self.rho)
            self._damp_imp = impedance_damping(self.vs_base, self._vs_slope)
            self._damp_tot = new_damp + self._damp_imp

            rel_delta_mod = abs((new_mod - shear_mod) / shear_mod)
            rel_delta_damp = abs((new_damp - damp_ratio) / damp_ratio)

            damp_ratio = new_damp
            shear_mod = new_mod

            count += 1
            if count > max_iterations:
                print(
                    "Warning: Maximum iterations reached. Equivalent linear procedure did not converge."
                )


mrd_testing = False
equivalent_linear_testing = False
k_y_testing = False


def some_ky_func(disp):
    initial = 0.15
    minimum = 0.05
    factor = 0.005
    exponent = -1.5
    value = max(factor * (disp + minimum) ** exponent + 0.4 * disp, minimum)
    return min(initial, value)


if __name__ == "__main__":
    if mrd_testing:
        strains = np.linspace(0.0001, 0.1, 1000)
        mod_reduction = []
        damping = []
        for strain in strains:
            mod_reduction.append(strain_mod_update(strain, 0.0005))
            damping.append(
                strain_damp_update(strain_mod_update(strain, 0.0005), strain, 0.0005)
            )
        darendelli = [mod_damp_testing(strain, 0.0005) for strain in strains]
        plt.close("all")
        # plt.plot(mod_reduction, damping)
        plt.semilogx(strains, mod_reduction)
        plt.semilogx(strains, damping)
        plt.show()
    else:
        histories = sample_ground_motions()
        ky_const = 0.15
        ky_interp = ([0.2, 0.3, 0.4, 0.5], [0.15, 0.14, 0.13, 0.12])
        ky_func = some_ky_func
        motion = histories["Chi-Chi_1999_TCU068-090"]
        t_step = motion[0][1] - motion[0][0]
        input_acc = motion[1] / 9.80665

        da = Decoupled(
            ky=ky_const,
            a_in=input_acc,
            dt=t_step,
            height=50.0,
            vs_slope=600.0,
            vs_base=600.0,
            damp_ratio=0.05,
            ref_strain=0.0005,
            scale_factor=1.0,
            soil_model="equivalent_linear",
            si_units=True,
            lite=False,
        )

        da.run_sliding_analysis()

        print(da.block_disp[-1] * 100)
