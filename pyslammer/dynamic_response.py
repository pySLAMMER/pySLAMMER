# This file is in the public domain.
import pyslammer as slam
from pyslammer.analysis import SlidingBlockAnalysis

import math

class DynamicResp(SlidingBlockAnalysis):
    def __init__(self):
        super().__init__()
        # main function parameters
        self.uwgt = 0.0
        self.height = 0.0
        self.vs = 0.0
        self.damp = 0.0
        self.damp1 = 0.0
        self.dt = 0.0
        self.scal = 0.0
        self.g = 0.0
        self.vr = 0.0
        self.vs1 = 0.0
        self.mmax = 0.0
        self.dv2 = True
        self.dv3 = False

        # main function variables
        self.Mtot = 0.0
        self.M = 0.0
        self.L = 0.0
        self.omega = 0.0
        self.beta = 0.0
        self.gamma = 0.0
        self.angle = 0.0
        self.qq = 0
        self.nmu = 0
        self.npts = 0

        self.rho = 0.0
        self.delt = 0.0
        self.dampf = 0.0
        self.damps = 0.0
        self.damps_prev = 0.0
        self.j = 0

        # slide=0 no sliding, slide=1 sliding
        # variable that end in 1 are for previous time step
        # variable that end in 2 are for current time step

        self.slide = False

        self.mx = 0.0
        self.mx1 = 0.0
        self.gameff1 = 0.0
        self.gamref = 0.0
        self.n = 0.0
        self.o = 0.0
        self.acc1 = 0.0
        self.acc2 = 0.0
        self.u1 = 0.0
        self.udot1 = 0.0
        self.udotdot1 = 0.0
        self.s = []
        self.u = []
        self.udot = []
        self.udotdot = []
        self.disp = []
        self.mu = []
        self.avgacc = []

        self.ain = []

    def eq_property(self):
        gameff2 = abs(self.gameff1) * 100.0
        vs2 = self.vs1 / math.sqrt(1.0 + (gameff2 / self.gamref))
        com1 = 1.0 / (1.0 + gameff2 / self.gamref)
        com2 = pow(com1, 0.1)

        self.damps = 0.0

        if not self.dv2:
            self.dampf = 0.0
        else:
            self.dampf = 55.016 * pow((self.vr / vs2), -0.9904)
            if self.dampf > 20.0:
                self.dampf = 20.0

        self.damps = 0.62 * com2 * (100.0 / math.pi * (4.0 * ((gameff2 - self.gamref * math.log((self.gamref + gameff2) / self.gamref)) / (gameff2 * gameff2 / (gameff2 + self.gamref))) - 2.0)) + 1.0
        damp2 = self.dampf + self.damps

        G1 = (self.uwgt / self.g) * self.vs * self.vs
        G2 = (self.uwgt / self.g) * vs2 * vs2

        l = (G1 - G2) / G1
        m = ((self.damps_prev - self.damps) / self.damps_prev)

        self.n = abs(l) * 100.0
        self.o = abs(m) * 100.0

        self.vs = vs2

        self.damps_prev = self.damps
        self.damp = damp2 * 0.01
        self.dampf = self.dampf * 0.01

    def residual_mu(self):
        if self.nmu > 1:
            if not self.slide and (abs(self.s[self.j - 1]) >= self.disp[self.qq - 1]):
                if self.qq <= (self.nmu - 1):
                    self.qq += 1

    def effstr(self):
        # effective shear strain calculation

        mx1 = 0.0
        mx = 0.0
        mmax = 0.0

        for jj in range(1, self.npts + 1):
            if jj == 1:
                mx1 = self.u[jj - 1]
                mx = self.u[jj - 1]
            else:
                if self.u[jj - 1] < 0:
                    if self.u[jj - 1] <= mx1:
                        mx1 = self.u[jj - 1]
                else:
                    if self.u[jj - 1] >= mx:
                        mx = self.u[jj - 1]

            if jj == self.npts:
                if abs(mx) > abs(mx1):
                    mmax = mx
                    self.gameff1 = 0.65 * 1.57 * mmax / self.height
                elif abs(mx) < abs(mx1):
                    mmax = mx1
                    self.gameff1 = 0.65 * 1.57 * mmax / self.height
                else:
                    if mx > 0:
                        mmax = mx
                        self.gameff1 = 0.65 * 1.57 * mmax / self.height
                    else:
                        mmax = mx1
                        self.gameff1 = 0.65 * 1.57 * mmax / self.height

        self.gameff1 = abs(self.gameff1)

    # calculate Kmax
    def avg_acc(self):
        mx1 = 0.0
        mx = 0.0

        for jj in range(1, self.npts + 1):
            if jj == 1:
                mx1 = self.avgacc[jj - 1]
                mx = self.avgacc[jj - 1]
            else:
                if self.avgacc[jj - 1] < 0.0:
                    if self.avgacc[jj - 1] <= mx1:
                        mx1 = self.avgacc[jj - 1]
                else:
                    if self.avgacc[jj - 1] >= mx:
                        mx = self.avgacc[jj - 1]

            if jj == self.npts:
                if abs(mx) > abs(mx1):
                    self.mmax = mx
                elif abs(mx) < abs(mx1):
                    self.mmax = mx1
                elif mx > 0.0:
                    self.mmax = mx
                else:
                    self.mmax = mx1

    def d_response(self):
        omega = math.pi * self.vs / (2.0 * self.height)

        khat = (omega * omega) + 2.0 * self.damp * omega * self.gamma / (self.beta * self.dt) + 1.0 / (self.beta * (self.dt * self.dt))
        a = 1.0 / (self.beta * self.dt) + 2.0 * self.damp * omega * self.gamma / self.beta
        b = 1.0 / (2.0 * self.beta) + self.dt * 2.0 * self.damp * omega * (self.gamma / (2.0 * self.beta) - 1.0)

        if self.j == 1:
            deltp = - self.L / self.M * (self.acc2 - self.acc1)
            deltu = deltp / khat
            deltudot = self.gamma / (self.beta * self.dt) * deltu
            u2 = deltu
            udot2 = deltudot
            udotdot2 = - (self.L / self.M) * self.acc2 - 2.0 * self.damp * omega * udot2 - (omega * omega) * u2
        else:
            deltp = - self.L / self.M * (self.acc2 - self.acc1) + a * self.udot1 + b * self.udotdot1
            deltu = deltp / khat
            deltudot = self.gamma / (self.beta * self.dt) * deltu - self.gamma / self.beta * self.udot1 + self.dt * (1.0 - self.gamma / (2.0 * self.beta)) * self.udotdot1
            deltudotdot = 1.0 / (self.beta * (self.dt * self.dt)) * deltu - 1.0 / (self.beta * self.dt) * self.udot1 - 0.5 / self.beta * self.udotdot1
            u2 = self.u1 + deltu
            udot2 = self.udot1 + deltudot
            udotdot2 = self.udotdot1 + deltudotdot

        self.avgacc[self.j - 1] = self.acc2
        self.u[self.j - 1] = u2
        self.udot[self.j - 1] = udot2
        self.udotdot[self.j - 1] = udotdot2
        self.avgacc[self.j - 1] = self.avgacc[self.j - 1] + self.L / self.Mtot * self.udotdot[self.j - 1]

    def d_setupstate(self):
        # set up state from previous time step
        if self.j == 1:
            self.u1 = 0.0
            self.udot1 = 0.0
            self.udotdot1 = 0.0
        else:
            self.u1 = self.u[self.j - 2]
            self.udot1 = self.udot[self.j - 2]
            self.udotdot1 = self.udotdot[self.j - 2]

        # set up acceleration loading

        if self.j == 1:
            self.acc1 = 0.0
            self.acc2 = self.ain[self.j - 1] * self.g * self.scal
        elif not self.slide:
            self.acc1 = self.ain[self.j - 2] * self.g * self.scal
            self.acc2 = self.ain[self.j - 1] * self.g * self.scal
            self.s[self.j - 1] = self.s[self.j - 2]
        else:
            self.acc1 = self.ain[self.j - 2] * self.g * self.scal
            self.acc2 = self.ain[self.j - 1] * self.g * self.scal

    def eq(self):
        t = 0

        while self.n > 5.0 or self.o > 5.0:
            for j in range(1, self.npts + 1):
                self.j = j
                self.d_setupstate()
                self.d_response()

            for j in range(1, self.npts + 1):
                self.j = j
                self.effstr()

            self.eq_property()

