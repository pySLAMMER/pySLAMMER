# Decoupled Block Analysis

import numpy as np
import pyslammer as slam
import matplotlib.pyplot as plt
import scipy.integrate as spint
from pyslammer.dynamic_response import DynamicResp
from pyslammer.constants import *



# 1 - PREVIOUS ITERATION
# 2 - CURRENT ITERATION

import math
import numpy as np

class Decoupled(DynamicResp):
    def __init__(self):
        super().__init__()
        self.deltacc = 0.0
        self.sdot = []
        self.time = 0.0

    def decoupled(self, ain_p, uwgt_p, height_p, vs_p, damp1_p, refstrain_p, dt_p, scal_p, g_p, vr_p, ca, dv3_p):
        # assign all passed parameters to the local data
        self.uwgt = uwgt_p  # UNIT WEIGHT? (MAYBE SPECIFIC WEIGHT)
        self.height = height_p  # HEIGHT OF SLOPE
        self.vs = vs_p  # SHEAR WAVE VELOCITY ABOVE SURFACE (IN SLIDING MASS)
        self.vs1 = self.vs  # COPY OF vs INTO 'PREVIOUS' ITERATION
        self.damp1 = damp1_p  # DAMPING RATIO
        self.damp = self.damp1  # COPY OF damp1
        self.dt = dt_p  # DT
        self.scal = scal_p  # SCALE FACTOR?
        self.g = g_p
        self.vr = vr_p  # SHEAR WAVE VELOCITY BELOW SURFACE (IN BASE)
        self.dv3 = dv3_p  # EQUIVALENT LINEAR (IF TRUE) OR LINEAR ELASTIC (IF FALSE)
        self.ain = ain_p  # GROUND MOTION ACCELERATION VALUES

        if 32.0 < self.g < 33.0:
            self.uwgt = 120.0
        else:
            self.uwgt = 20.0

        # init graphing
        self.set_value_size(self.dt)

        # copy ca into disp and mu
        # mu AND disp RELATED TO CRITICAL ACCELERATION. LENGTH > 1 IF CRITICAL ACCELERATION VARIES WITH DISPLACEMENT
        self.disp = ca[0]#[row[0] for row in ca]
        self.mu = ca[1]#[row[1] for row in ca]

        self.nmu = len(ca)  # LENGTH OF mu TABLE

        self.npts = len(self.ain)  # NUMBER OF POINTS IN GROUND MOTION

        self.avgacc = [0.0] * self.npts
        self.s = [0.0] * self.npts
        self.sdot = [0.0] * self.npts
        self.u = [0.0] * self.npts
        self.udot = [0.0] * self.npts
        self.udotdot = [0.0] * self.npts

        self.deltacc = 0.0
        # u1, udot, udotdot1 GROUND DISP, VELOCITY, ACCELERATION RESPECTIVELY
        self.u1 = 0.0
        self.udot1 = 0.0
        self.udotdot1 = 0.0

        self.acc1 = 0.0
        self.acc2 = 0.0
        self.mx = 0.0
        self.mx1 = 0.0
        self.mmax = 0.0
        self.gameff1 = 0.0
        self.n = 100.0
        self.o = 100.0

        self.rho = self.uwgt / self.g  # DENSITY

        self.dampf = 55.016 * (self.vr / self.vs) ** -0.9904 / 100.0
        if self.dampf > 0.2:
            self.dampf = 0.2

        self.scal *= -1.0

        # for each mode calculate constants.py for Slammer algorithm

        self.beta = 0.25
        self.gamma = 0.5
        self.Mtot = self.rho * self.height
        self.slide = True
        self.qq = 1

        self.omega = math.pi * self.vs / (2.0 * self.height)
        # L AND M CONSTANTS FROM RATHJE 1999?
        self.L = -2.0 * self.rho * self.height / math.pi * math.cos(math.pi)
        self.M = self.rho * self.height / 2.0

        self.n = 100.0
        self.o = 100.0
        self.gamref = refstrain_p
        self.damp = self.damp1 + self.dampf

        # loop for time steps in time histories

        # for equivalent linear
        if self.dv3:
            self.eq()

        self.omega = math.pi * self.vs / (2.0 * self.height)

        # calculate final dynamic response using original prop's for LE analysis and EQL properties for EQL analysis
        for j in range(1, self.npts + 1):
            self.d_setupstate()
            self.d_response()

        self.slide = False
        self.time = 0.0

        self.avg_acc()

        self._kmax = self.mmax
        self._vs = self.vs
        self._damp = self.damp
        self._dampf = self.dampf
        self._omega = self.omega

        # calculate decoupled displacements
        for j in range(1, self.npts + 1):
            self.d_sliding(j)
            # self.store(abs(self.s[j - 1]))
            self.residual_mu()

        # self.end(abs(self.s[self.npts - 1]))
        return abs(self.s[self.npts - 1])

    def d_sliding(self, j):
        # calculate decoupled displacements

        if j == 1:
            deltacc = self.avgacc[j - 1]
        else:
            deltacc = self.avgacc[j - 1] - self.avgacc[j - 2]

        if j == 1:
            self.sdot[j - 1] = 0
            self.s[j - 1] = 0
        elif not self.slide:
            self.sdot[j - 1] = 0
            self.s[j - 1] = self.s[j - 2]
        else:
            self.sdot[j - 1] = self.sdot[j - 2] + (self.mu[self.qq - 1] * self.g - self.avgacc[j - 2]) * self.dt - 0.5 * deltacc * self.dt
            self.s[j - 1] = self.s[j - 2] - self.sdot[j - 2] * self.dt - 0.5 * self.dt * self.dt * (self.mu[self.qq - 1] * self.g - self.avgacc[j - 2]) + deltacc * self.dt * self.dt / 6.0

        if not self.slide:
            if self.avgacc[j - 1] > self.mu[self.qq - 1] * self.g:
                self.slide = True
        else:
            if self.sdot[j - 1] >= 0.0:
                self.slide = False

                if j == 1:
                    self.s[j - 1] = 0
                else:
                    self.s[j - 1] = self.s[j - 2]

                self.sdot[j - 1] = 0.0



if __name__ == "__main__":
    histories = slam.sample_ground_motions()
    ky = 0.02
    motion = histories["Chi-Chi_1999_TCU068-090"]
    dt = motion[0][1] - motion[0][0]

    da = Decoupled()
    out = da.decoupled(ain_p=motion[1],
                 uwgt_p=20.0,
                 height_p=50.0,
                 vs_p=600.0,
                 damp1_p=0.05,
                 refstrain_p=0.01,
                 dt_p=dt,
                 scal_p=1.0,
                 g_p=9.80665,
                 vr_p=600.0,
                 ca=[[1],[ky]],
                 dv3_p=False)

    print(out)
    # single_result = slam.SlidingBlockAnalysis(histories[motion], ky, analysis_type="decoupled")
    # single_result = decoupled_analysis(motion, ky)
    # plt.close('all')
    # fig, ax = plt.subplots()
    # ax.plot(single_result[0], motion[1], label='Block Displacement')
    # ax.plot(single_result[0], single_result[1], label='Block Displacement')
    # plt.show()

# def decoupled_analysis(time_history: np.ndarray, acc_crit: float):
#     """
#     Perform decoupled block analysis.
#     Args:
#         time_history:
#         acc_crit:
#
#     Returns:
#
#     """
#     if time_history is None:
#         return
#     else:
#         pass
#     acc_crit = acc_crit * G_EARTH
#     time = time_history[0][:]
#     gnd_acc = time_history[1][:]
#     block_disp = []
#     block_vel = []
#     block_acc = []
#     tol = 0.00001
#
#     height = 50.0 # meters
#     vs_block = 600 # m/s
#     vs_base = 600 # m/s
#     rho_block = 2000 # kg/m^3
#     rho_base = 2000 # kg/m^3
#     damping = 0.05
#     ref_strain = 0.01
#
#     avg_acc = np.zeros(len(gnd_acc))
#
#     dt = time[1] - time[0]  # D
#     pos_curr = 0  # U
#     vel_curr = 0  # V
#     pos_prev = 0  # Q
#     vel_prev = 0  # R
#     acc_prev = 0  # S
#     acc_curr = 0  # Y
#     for i in range(len(gnd_acc)):
#         gnd_acc_curr = gnd_acc[i]
#         if vel_curr < tol:
#             if abs(gnd_acc_curr) > acc_crit:
#                 n = gnd_acc_curr / abs(gnd_acc_curr)
#             else:
#                 n = gnd_acc_curr / acc_crit
#         else:
#             n = 1
#         acc_curr = gnd_acc_curr - n * acc_crit
#         vel_curr = vel_prev + (dt / 2) * (acc_curr + acc_prev)
#         if vel_curr > 0:
#             pos_curr = pos_prev + (dt / 2) * (vel_curr + vel_prev)
#         else:  # P
#             vel_curr = 0
#             acc_curr = 0
#         pos_prev = pos_curr
#         vel_prev = vel_curr
#         acc_prev = acc_curr
#         block_disp.append(pos_curr)
#         block_vel.append(vel_curr)
#         block_acc.append(acc_curr)
#     # print('Displacement: ' + '{:.4f}'.format(block_disp[-1] * M_TO_CM) + ' cm')
#     block_data = np.vstack((time, block_disp, block_vel))
#     return block_data