import numpy as np
from pyslammer.decoupled_analysis import DeCoupledCommon

class Coupled(DeCoupledCommon):
    def __init__(self):
        self.s1 = self.sdot1 = self.sdotdot1 = 0.0
        self.s2 = self.sdot2 = self.sdotdot2 = 0.0
        self.u2 = self.udot2 = self.udotdot2 = self.baseacc = 0.0
        self.basef = self.acc11 = self.acc22 = self.normalf1 = self.normalf2 = 0.0
        self.COS = self.SIN = self.gSIN = self.gCOS = 0.0

    def Coupled(self, ain_p, uwgt_p, height_p, vs_p, damp1_p, refstrain_p, dt_p, scal_p, g_p, vr_p, ca, dv3_p):
        # assign all passed parameters to the local data
        self.uwgt = uwgt_p
        self.height = height_p
        self.vs = vs_p
        self.vs1 = vs_p
        self.damp1 = damp1_p
        self.damp = self.damp1
        self.dt = dt_p
        self.scal = scal_p
        self.g = g_p
        self.vr = vr_p
        self.dv3 = dv3_p
        self.ain = ain_p

        # init graphing
        self.setValueSize(dt_p)

        # copy ca into disp and mu
        self.disp = np.array([row[0] for row in ca])
        self.mu = np.array([row[1] for row in ca])

        self.npts = len(ain_p)

        # precompute some numbers
        self.COS = np.cos(self.angle * np.pi / 180.0)
        self.SIN = np.sin(self.angle * np.pi / 180.0)

        self.gCOS = self.g * self.COS
        self.gSIN = self.g * self.SIN

        self.delt = 0.0
        self.j = 0

        self.initialize_variables()

        # these are previous iteration value
        self.rho = self.uwgt / self.g
        self.nmu = len(ca)

        self.dampf = 55.016 * (vr_p / vs_p) ** -0.9904 / 100.0
        if self.dampf > 0.2:
            self.dampf = 0.2

        # for each mode calculate constants.py for SLAMMER algorithm
        self.beta = 0.25
        self.gamma = 0.5
        self.Mtot = self.rho * self.height
        self.slide = False
        self.normalf2 = 0.0
        self.angle = 0.0
        self.qq = 1
        self.omega = np.pi * self.vs / (2.0 * self.height)
        self.L = 2.0 * self.rho * self.height / np.pi
        self.M = self.rho * self.height / 2.0

        self.damp = self.damp1 + self.dampf
        self.n = 100.0
        self.o = 100.0
        self.gamref = refstrain_p

        # finding equivalent linear properties of soil
        if dv3_p:
            self.eq()

        # Calculate decoupled dynamic response and Kmax using LE properties or final EQL properties
        for self.j in range(1, self.npts + 1):
            self.d_setupstate()
            self.d_response()

        self.avg_acc()

        # loop for time steps in time histories
        self.initialize_variables()

        self._kmax = self.mmax
        self._vs = self.vs
        self._damp = self.damp
        self._dampf = self.dampf
        self._omega = self.omega

        for j in range(self.npts):
            self.s[j] = 0
            self.u[j] = 0

        for self.j in range(1, self.npts + 1):
            self.coupled_setupstate(self.j)

            # solve for u, udot, udotdot at next time step
            self.solvu(self.j)
            self.udotdot[self.j - 1] = self.udotdot2

            # update sliding acceleration based on calc'd response
            self.c_slideacc()

            # check if sliding has started
            self.c_slidingcheck()

            self.s[self.j - 1] = self.s2

            self.store(abs(self.s2))

            self.residual_mu()

        self.end(abs(self.s2))
        return abs(self.s2)

    def initialize_variables(self):
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

    def slidestop(self):
        ddt = acc11 = acc22 = acc1b = delt = dd = 0.0
        khat = deltp = a = b = 0.0

        delt = self.dt

        # Time of end of sliding is taken as where sdot=0 from previous analysis
        dd = -self.sdot1 / (self.sdot2 - self.sdot1)
        ddt = dd * delt
        acc11 = self.gSIN - self.mu[self.qq - 1] * (self.gCOS + self.ain[self.j - 1] * self.scal * self.gSIN)
        acc1b = self.ain[self.j - 2] * self.g * self.scal + dd * (self.ain[self.j - 1] - self.ain[self.j - 2]) * self.g * self.scal
        acc22 = self.gSIN - self.mu[self.qq - 1] * (self.gCOS + acc1b * self.SIN)

        # if dd=0, sliding has already stopped and skip this solution
        if dd == 0:
            return

        self.solvu(self.j)
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
        acc22 = self.ain[self.j - 1] * self.gCOS * self.scal

        khat = 1.0 + 2.0 * self.damp * self.omega * self.gamma * ddt + (self.omega ** 2) * self.beta * (ddt ** 2)
        a = (1.0 - (self.L ** 2) / (self.Mtot * self.M)) + 2.0 * self.damp * self.omega * ddt * (self.gamma - 1.0) + (self.omega ** 2) * (ddt ** 2) * (self.beta - 0.5)
        b = (self.omega ** 2) * ddt
        deltp = - self.L / self.M * (acc22 - acc11) + a * (self.udotdot1) - b * (self.udot1)
        self.udotdot2 = deltp / khat

        self.udot2 = self.udot1 + (1.0 - self.gamma) * ddt * (self.udotdot1) + self.gamma * ddt * (self.udotdot2)
        self.u2 = self.u1 + self.udot1 * ddt + (0.5 - self.beta) * (ddt ** 2) * (self.udotdot1) + self.beta * (ddt ** 2) * (self.udotdot2)

    def solvu(self, jj):
        khat = a = b = deltp = deltu = deltudot = d1 = 0.0

        delt = self.dt

        if self.slide:
            d1 = 1.0 - (self.L ** 2) / (self.M * self.Mtot)
        else:
            d1 = 1.0

        khat = (self.omega ** 2) + 2.0 * self.damp * self.omega * self.gamma / (self.beta * delt) + d1 / (self.beta * (delt ** 2))
        a = d1 / (self.beta * delt) + 2.0 * self.damp * self.omega * self.gamma / self.beta
        b = d1 / (2.0 * self.beta) + delt * 2.0 * self.damp * self.omega * (self.gamma / (2.0 * self.beta) - 1.0)

        if jj == 1:
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

        self.u[jj - 1] = self.u2

    def coupled_setupstate(self, jj):
        # set up state from previous time step
        if jj == 1:
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
        self.normalf2 = self.Mtot * self.gCOS + self.Mtot * self.ain[jj - 1] * self.scal * self.gSIN

        if jj == 1:
            self.acc11 = 0.0
            self.acc22 = self.ain[jj - 1] * self.gCOS * self.scal
        elif not self.slide:
            self.acc11 = self.ain[jj - 2] * self.gCOS * self.scal
            self.acc22 = self.ain[jj - 1] * self.gCOS * self.scal
        else:
            self.acc11 = self.gSIN - self.mu[self.qq - 1] * self.normalf1 / self.Mtot
            self.acc22 = self.gSIN - self.mu[self.qq - 1] * self.normalf2 / self.Mtot

    def c_slidingcheck(self):
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

    def c_slideacc(self):
        # update sliding acceleration based on calc'd response
        if self.slide:
            self.sdotdot2 = -self.ain[self.j - 1] * self.gCOS * self.scal - self.mu[self.qq - 1] * self.normalf2 / self.Mtot - self.L * self.udotdot2 / self.Mtot + self.gSIN

        # calc. base force based on udotdot calc
        self.basef = -self.Mtot * self.ain[self.j - 1] * self.gCOS * self.scal - self.L * self.udotdot2 + self.Mtot * self.gSIN

        # If sliding is occurring, integrate sdotdot, using trapezoid rule, to get sdot and s.
        if self.slide:
            self.sdot2 = self.sdot1 + 0.5 * self.dt * (self.sdotdot2 + self.sdotdot1)
            self.s2 = self.s1 + 0.5 * self.dt * (self.sdot2 + self.sdot1)

