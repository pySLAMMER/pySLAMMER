import numpy as np
from pyslammer.decoupled_analysis import Decoupled

class Coupled(Decoupled):
    def __init__(self,
                 k_y: float or tuple[list[float], list[float]] or tuple[np.ndarray, np.ndarray] or callable,
                 a_in: list[float] or np.ndarray,
                 dt: float,
                 height: int or float,
                 vs_slope: int or float,
                 vs_base: int or float,
                 damp_ratio: float,
                 ref_strain: float):
        super().__init__(k_y, a_in, dt, height, vs_slope, vs_base, damp_ratio, ref_strain)

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


    def sliding(self,i):
        self.coupled_setupstate(i)

        # solve for x_resp, v_resp, a_resp at next time step
        self.solvu(i)
        self.udotdot[i - 1] = self.udotdot2

        # update sliding acceleration based on calc'd response
        self.c_slideacc(i)

        # check if sliding has started
        self.c_slidingcheck(i)

        self.s[i - 1] = self.s2


    def slidestop(self, i):
        ddt = acc11 = acc22 = acc1b = delt = dd = 0.0
        khat = deltp = a = b = 0.0

        delt = self.dt

        # Time of end of sliding is taken as where block_vel=0 from previous analysis
        dd = -self.sdot1 / (self.sdot2 - self.sdot1)
        ddt = dd * delt
        acc11 = self.gSIN - self.mu[self.qq - 1] * (self.gCOS + self.ain[i - 1] * self.scal * self.gSIN)
        acc1b = self.ain[i - 2] * self.g * self.scal + dd * (self.ain[i - 1] - self.ain[i - 2]) * self.g * self.scal
        acc22 = self.gSIN - self.mu[self.qq - 1] * (self.gCOS + acc1b * self.SIN)

        # if dd=0, sliding has already stopped and skip this solution
        if dd == 0:
            return

        self.solvu(i)
        self.u1 = self.u2
        self.udot1 = self.udot2
        self.udotdot1 = self.udotdot2
        self.normalf2 = self.Mtot * self.gCOS + self.Mtot * acc1b * self.SIN
        self.sdotdot2 = -acc1b * self.COS - self.mu[self.qq - 1] * self.normalf2 / self.Mtot - self.L * self.udotdot2 / self.Mtot + self.gSIN
        self.sdot2 = self.sdot1 + 0.5 * ddt * (self.sdotdot2 + self.sdotdot1)
        self.s2 = self.s1 + 0.5 * ddt * (self.sdot1 + self.sdot2)

        # Solve for non sliding response during remaining part of dt
        ddt = (1.0 - dd) * delt
        self.slide = False
        acc11 = acc22
        acc22 = self.ain[i - 1] * self.gCOS * self.scal

        khat = 1.0 + 2.0 * self.damp * self.omega * self.gamma * ddt + (self.omega ** 2) * self.beta * (ddt ** 2)
        a = (1.0 - (self.L ** 2) / (self.Mtot * self.M)) + 2.0 * self.damp * self.omega * ddt * (self.gamma - 1.0) + (self.omega ** 2) * (ddt ** 2) * (self.beta - 0.5)
        b = (self.omega ** 2) * ddt
        deltp = - self.L / self.M * (acc22 - acc11) + a * (self.udotdot1) - b * (self.udot1)
        self.udotdot2 = deltp / khat

        self.udot2 = self.udot1 + (1.0 - self.gamma) * ddt * (self.udotdot1) + self.gamma * ddt * (self.udotdot2)
        self.u2 = self.u1 + self.udot1 * ddt + (0.5 - self.beta) * (ddt ** 2) * (self.udotdot1) + self.beta * (ddt ** 2) * (self.udotdot2)

    def solvu(self, i):
        khat = a = b = deltp = deltu = deltudot = d1 = 0.0

        delt = self.dt

        if self.slide:
            d1 = 1.0 - (self.L ** 2) / (self.M * self.Mtot)
        else:
            d1 = 1.0

        khat = (self.omega ** 2) + 2.0 * self.damp * self.omega * self.gamma / (self.beta * delt) + d1 / (self.beta * (delt ** 2))
        a = d1 / (self.beta * delt) + 2.0 * self.damp * self.omega * self.gamma / self.beta
        b = d1 / (2.0 * self.beta) + delt * 2.0 * self.damp * self.omega * (self.gamma / (2.0 * self.beta) - 1.0)

        if i == 1:
            deltp = -self.L / self.M * (self.acc22 - self.acc11)
            deltu = deltp / khat
            deltudot = self.gamma / (self.beta * delt) * deltu
            self.u2 = deltu
            self.udot2 = deltudot
            self.udotdot2 = (-(self.L / self.M) * self.acc22 - 2.0 * self.damp * self.omega * self.udot2 - (self.omega ** 2) * self.u2) / d1
        else:
            deltp = -self.L / self.M * (self.acc22 - self.acc11) + a * self.udot1 + b * self.udotdot1
            deltu = deltp / khat
            deltudot = self.gamma / (self.beta * delt) * deltu - self.gamma / self.beta * self.udot1 + delt * (1.0 - self.gamma / (2.0 * self.beta)) * self.udotdot1
            self.u2 = self.u1 + deltu
            self.udot2 = self.udot1 + deltudot
            self.udotdot2 = (-(self.L / self.M) * self.acc22 - 2.0 * self.damp * self.omega * self.udot2 - (self.omega ** 2) * self.u2) / d1

        self.u[i - 1] = self.u2

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

        # Set up acceleration loading. Normal force corrected for vertical component of accel.
        self.normalf2 = self.Mtot * self.gCOS + self.Mtot * self.ain[i - 1] * self.scal * self.gSIN

        if i == 1:
            self.acc11 = 0.0
            self.acc22 = self.ain[i - 1] * self.gCOS * self.scal
        elif not self.slide:
            self.acc11 = self.ain[i - 2] * self.gCOS * self.scal
            self.acc22 = self.ain[i - 1] * self.gCOS * self.scal
        else:
            self.acc11 = self.gSIN - self.mu[self.qq - 1] * self.normalf1 / self.Mtot
            self.acc22 = self.gSIN - self.mu[self.qq - 1] * self.normalf2 / self.Mtot

    def c_slidingcheck(self, i):
        # check if sliding has started
        if not self.slide:
            if self.basef > self.mu[self.qq - 1] * self.normalf2:
                self.slide = True
        elif self.slide:
            if self.sdot2 <= 0.0:
                self.slidestop()
                self.slide = False
                self.sdot2 = 0.0
                self.sdotdot2 = 0.0

    def c_slideacc(self, i):
        # update sliding acceleration based on calc'd response
        if self.slide:
            self.sdotdot2 = -self.ain[i - 1] * self.gCOS * self.scal - self.mu[self.qq - 1] * self.normalf2 / self.Mtot - self.L * self.udotdot2 / self.Mtot + self.gSIN

        # calc. base force based on a_resp calc
        self.basef = -self.Mtot * self.ain[i - 1] * self.gCOS * self.scal - self.L * self.udotdot2 + self.Mtot * self.gSIN

        # If sliding is occurring, integrate sdotdot, using trapezoid rule, to get block_vel and block_disp.
        if self.slide:
            self.sdot2 = self.sdot1 + 0.5 * self.dt * (self.sdotdot2 + self.sdotdot1)
            self.s2 = self.s1 + 0.5 * self.dt * (self.sdot2 + self.sdot1)

