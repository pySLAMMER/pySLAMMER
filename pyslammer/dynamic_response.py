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
        self.eqvlnr = False

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



