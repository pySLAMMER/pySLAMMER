# This file is in the public domain.

# import decimal
# from jfree.data.xy import XYSeries


class SlidingBlockAnalysis:
    # fmtFive = decimal.Decimal("0.00000")
    # fmtFour = decimal.Decimal("0.0000")
    # fmtThree = decimal.Decimal("0.000")
    # fmtTwo = decimal.Decimal("0.00")
    # fmtOne = decimal.Decimal("0.0")
    # fmtZero = decimal.Decimal("0")




    # testing = False

    def __init__(self):
        self.method = None
        self.ky = None
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

        self.time = 0
        self.dint = 0
        self.last = 0
        self.skipped = False
        self.timeStor = 0
        # self.graphData = None
        self._kmax = 0
        self._damp = 0
        self._vs = 0
        self._dampf = 0
        self._omega = 0

    # def set_value_size(self, Dint):
    #     if self.testing:
    #         return
    #
    #     self.time = 0
    #     self.dint = Dint
    #     # self.graphData = XYSeries("")
    #     self.last = -1
    #     self.skipped = False
        # self.timeStor = 0

    # def store(self, d):
    #     if self.testing:
    #         return
    #
    #     if d == self.last:
    #         self.skipped = True
    #     else:
    #         if self.skipped:
    #             self.real_store(self.last, self.time - self.dint)
    #             self.skipped = False
    #
    #         if self.time >= (self.timeStor + self.interval):
    #             self.real_store(d, self.time)
    #             self.timeStor = self.time
    #
    #     self.time += self.dint

    # def end(self, d):
    #     if self.testing:
    #         return
    #
    #     if self.skipped:
    #         self.real_store(self.last, self.time - self.dint)
    #     self.real_store(d, self.time)

    # def real_store(self, d, time):
    #     try:
    #         self.graphData.add(float(time), float(d))
    #     except Exception:
    #         pass
    #     self.last = d

    # # Overridden functions
    # def Decoupled(self, ain_p, uwgt_p, height_p, vs_p, damp1_p, refstrain, dt_p, scal_p, g_p, vr_p, ca, dv3_p):
    #     return 0
    #
    # def Coupled(self, ain_p, uwgt_p, height_p, vs_p, damp1_p, refstrain, dt_p, scal_p, g_p, vr_p, ca, dv3_p):
    #     return 0
    #
    # def SlammerRigorous(self, data, d, disp, mult, dualSlope, ta, unitMult):
    #     return 0

    # Standard functions
    # @staticmethod
    # def sign(val):
    #     return 1 if val >= 0 else -1

