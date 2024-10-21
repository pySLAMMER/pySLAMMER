import numpy as np

import pyslammer as slam
import matplotlib.pyplot as plt

from pyslammer.decoupled_analysis import Decoupled
from pyslammer.constants import *
import math


class Coupled(Decoupled):
    def __init__(self,
                 ky: float or tuple[list[float], list[float]] or tuple[np.ndarray, np.ndarray] or callable,
                 a_in: list[float] or np.ndarray,
                 dt: float,
                 height: int or float,
                 vs_slope: int or float,
                 vs_base: int or float,
                 damp_ratio: float,
                 ref_strain: float,
                 scale_factor: float = 1,
                 soil_model: str = "linear_elastic",
                 si_units: bool = True,
                 lite: bool = False):
        super().__init__(ky, a_in, dt, height, vs_slope, vs_base, damp_ratio, ref_strain, scale_factor, soil_model,
                         si_units, lite)

        self.s1 = self.sdot1 = self.sdotdot1 = 0.0
        self.s2 = self.sdot2 = self.sdotdot2 = 0.0
        self.u1 = self.udot1 = self.udotdot1 = 0.0
        self.u2 = self.udot2 = self.udotdot2 = 0.0
        self.baseacc = self.basef = self.acc11 = self.acc22 = 0.0
        self.normalf1 = self.normalf2 = self.gameff1 = 0.0
        self.mx = self.mx1 = self.mmax = 0.0
        self.s = np.zeros(self.npts)
        self.u = np.zeros(self.npts)
        self.udotdot = np.zeros(self.npts)
        self.avgacc = np.zeros(self.npts)
        self.udot = np.zeros(self.npts)
        self.angle = 0
        self.COS = math.cos(self.angle * math.pi / 180.0)
        self.SIN = math.sin(self.angle * math.pi / 180.0)

        self.gCOS = self.g * self.COS
        self.gSIN = self.g * self.SIN

        self.beta = 0.25  # TODO: move to global constants
        self.gamma = 0.5  # TODO: move to global constants

        self.block_acc = np.zeros(self.npts)

        if type(self) is Coupled:
            self.run_sliding_analysis()
        self.ground_acc = a_in * self.g


    def run_sliding_analysis(self):  # TODO: add ca to inputs
        if self.soil_model == "equivalent_linear":
            self.equivalent_linear()

        for i in range(1, self.npts + 1):
            self.dynamic_response(i)

        # calculate decoupled displacements
        for i in range(1, self.npts + 1):
            self.coupled_sliding(i)

        self.max_sliding_disp = self.block_disp[-1]
        # return self.max_sliding_disp
        self.block_disp = self.s

    def coupled_sliding(self, i):
        self.coupled_setupstate(i)
        # solve for x_resp, v_resp, a_resp at next time step
        self.solvu(i)
        self.udotdot[i - 1] = self.udotdot2

        # update sliding acceleration based on calc'd response
        self.c_slideacc(i)

        # check if sliding has started
        self.c_slidingcheck(i)
        self.block_acc[i-1] = self.acc22 - self.sdotdot2

        self.s[i - 1] = self.s2

    def coupled_setupstate(self, i):
        # set up state from previous time step
        if i == 1:
            self.u1 = self.udot1 = self.udotdot1 = self.s1 = self.sdot1 = self.sdotdot1 = self.normalf1 = 0.0
        else:
            self.u1 = self.u2
            self.udot1 = self.udot2
            self.udotdot1 = self.udotdot2
            self.s1 = self.s2
            self.sdot1 = self.sdot2
            self.sdotdot1 = self.sdotdot2
            self.normalf1 = self.normalf2

        # Set up acceleration loading. Normal force corrected for vertical component of a_in.
        self.normalf2 = self.mass * self.gCOS + self.mass * self.a_in[i - 1] * self.scale_factor * self.gSIN

        if i == 1:
            self.acc11 = 0.0
            self.acc22 = self.a_in[i - 1] * self.gCOS * self.scale_factor
        elif not self._slide:
            self.acc11 = self.a_in[i - 2] * self.gCOS * self.scale_factor
            self.acc22 = self.a_in[i - 1] * self.gCOS * self.scale_factor
        else:
            self.acc11 = self.gSIN - self.k_y(self.s[i - 2]) * self.normalf1 / self.mass
            self.acc22 = self.gSIN - self.k_y(self.s[i - 2]) * self.normalf2 / self.mass

    def solvu(self, i):
        khat = a = b = deltp = deltu = deltudot = d1 = 0.0

        delt = self.dt

        if self._slide:
            d1 = 1.0 - (self.L1 ** 2) / (self.M1 * self.mass)
        else:
            d1 = 1.0

        khat = (self._omega ** 2) + 2.0 * self._damp_tot * self._omega * self.gamma / (self.beta * delt) + d1 / (
                    self.beta * (delt ** 2))
        a = d1 / (self.beta * delt) + 2.0 * self._damp_tot * self._omega * self.gamma / self.beta
        b = d1 / (2.0 * self.beta) + delt * 2.0 * self._damp_tot * self._omega * (self.gamma / (2.0 * self.beta) - 1.0)

        if i == 1:
            deltp = -self.L1 / self.M1 * (self.acc22 - self.acc11)
            deltu = deltp / khat
            deltudot = self.gamma / (self.beta * delt) * deltu
            self.u2 = deltu
            self.udot2 = deltudot
            self.udotdot2 = (-(self.L1 / self.M1) * self.acc22 - 2.0 * self._damp_tot * self._omega * self.udot2 - (
                        self._omega ** 2) * self.u2) / d1
        else:
            deltp = -self.L1 / self.M1 * (self.acc22 - self.acc11) + a * self.udot1 + b * self.udotdot1
            deltu = deltp / khat
            deltudot = self.gamma / (self.beta * delt) * deltu - self.gamma / self.beta * self.udot1 + delt * (
                        1.0 - self.gamma / (2.0 * self.beta)) * self.udotdot1
            self.u2 = self.u1 + deltu
            self.udot2 = self.udot1 + deltudot
            self.udotdot2 = (-(self.L1 / self.M1) * self.acc22 - 2.0 * self._damp_tot * self._omega * self.udot2 - (
                        self._omega ** 2) * self.u2) / d1

        self.u[i - 1] = self.u2

    def c_slideacc(self, i):
        # update sliding acceleration based on calc'd response
        if self._slide:
            self.sdotdot2 = -self.a_in[i - 1] * self.gCOS * self.scale_factor - self.k_y(
                self.s[i - 2]) * self.normalf2 / self.mass - self.L1 * self.udotdot2 / self.mass + self.gSIN

        # calc. base force based on a_resp calc
        self.basef = -self.mass * self.a_in[
            i - 1] * self.gCOS * self.scale_factor - self.L1 * self.udotdot2 + self.mass * self.gSIN

        # If sliding is occurring, integrate sdotdot, using trapezoid rule, to get block_vel and block_disp.
        if self._slide:
            self.sdot2 = self.sdot1 + 0.5 * self.dt * (self.sdotdot2 + self.sdotdot1)
            self.s2 = self.s1 + 0.5 * self.dt * (self.sdot2 + self.sdot1)

    def c_slidingcheck(self, i):
        # check if sliding has started
        if not self._slide:
            if self.basef > self.k_y(self.s[i - 2]) * self.normalf2:
                self._slide = True
        elif self._slide:
            if self.sdot2 <= 0.0:
                self.slidestop(i)
                self._slide = False
                self.sdot2 = 0.0
                self.sdotdot2 = 0.0

    def slidestop(self, i):
        ddt = acc11 = acc22 = acc1b = delt = dd = 0.0
        khat = deltp = a = b = 0.0

        delt = self.dt

        # Time of end of sliding is taken as where block_vel=0 from previous analysis
        dd = -self.sdot1 / (self.sdot2 - self.sdot1)
        ddt = dd * delt
        acc11 = self.gSIN - self.k_y(self.s[i - 2]) * (self.gCOS + self.a_in[i - 1] * self.scale_factor * self.gSIN)
        acc1b = self.a_in[i - 2] * self.g * self.scale_factor + dd * (
                    self.a_in[i - 1] - self.a_in[i - 2]) * self.g * self.scale_factor
        acc22 = self.gSIN - self.k_y(self.s[i - 2]) * (self.gCOS + acc1b * self.SIN)

        # if dd=0, sliding has already stopped and skip this solution
        if dd == 0:
            return

        self.solvu(i)
        self.u1 = self.u2
        self.udot1 = self.udot2
        self.udotdot1 = self.udotdot2
        self.normalf2 = self.mass * self.gCOS + self.mass * acc1b * self.SIN
        self.sdotdot2 = -acc1b * self.COS - self.k_y(
            self.s[i - 2]) * self.normalf2 / self.mass - self.L1 * self.udotdot2 / self.mass + self.gSIN
        self.sdot2 = self.sdot1 + 0.5 * ddt * (self.sdotdot2 + self.sdotdot1)
        self.s2 = self.s1 + 0.5 * ddt * (self.sdot1 + self.sdot2)

        # Solve for non sliding response during remaining part of dt
        ddt = (1.0 - dd) * delt
        self._slide = False
        acc11 = acc22
        acc22 = self.a_in[i - 1] * self.gCOS * self.scale_factor

        khat = 1.0 + 2.0 * self._damp_tot * self._omega * self.gamma * ddt + (self._omega ** 2) * self.beta * (ddt ** 2)
        a = (1.0 - (self.L1 ** 2) / (self.mass * self.M1)) + 2.0 * self._damp_tot * self._omega * ddt * (
                    self.gamma - 1.0) + (self._omega ** 2) * (ddt ** 2) * (self.beta - 0.5)
        b = (self._omega ** 2) * ddt
        deltp = - self.L1 / self.M1 * (acc22 - acc11) + a * (self.udotdot1) - b * (self.udot1)
        self.udotdot2 = deltp / khat

        self.udot2 = self.udot1 + (1.0 - self.gamma) * ddt * (self.udotdot1) + self.gamma * ddt * (self.udotdot2)
        self.u2 = self.u1 + self.udot1 * ddt + (0.5 - self.beta) * (ddt ** 2) * (self.udotdot1) + self.beta * (
                    ddt ** 2) * (self.udotdot2)


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
    histories = slam.sample_ground_motions()
    ky_const = 0.15
    ky_interp = ([0.2, 0.3, 0.4, 0.5], [0.15, 0.14, 0.13, 0.12])
    ky_func = some_ky_func
    motion = histories["Chi-Chi_1999_TCU068-090"]
    # t_step = motion[0][1] - motion[0][0]
    # input_acc = motion[1] / 9.80665

    ca = slam.Coupled(ky=ky_func,
                      a_in=motion.accel,
                      dt=motion.dt,
                      height=50.0,
                      vs_slope=600.0,
                      vs_base=600.0,
                      damp_ratio=0.05,
                      ref_strain=0.0005,
                      scale_factor=1.0,
                      soil_model="equivalent_linear",
                      si_units=True,
                      lite=False)

    ca.run_sliding_analysis()
    print(ca.s[-1] * 100)