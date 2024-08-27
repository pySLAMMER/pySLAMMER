# Decoupled Block Analysis

import numpy as np
import pyslammer as slam
import matplotlib.pyplot as plt
import scipy.integrate as spint

from pyslammer.analysis import SlidingBlockAnalysis
from pyslammer.dynamic_response import DynamicResp
from pyslammer.constants import *



# 1 - PREVIOUS ITERATION
# 2 - CURRENT ITERATION

import math
import numpy as np

class Decoupled(SlidingBlockAnalysis):
    def __init__(self,
                 k_y: float,# TODO: or tuple[list[float], list[float]] or tuple[np.ndarray,np.ndarray] or callable(float),
                 a_in: list[float] or np.ndarray,
                 dt: float,
                 height: int or float,
                 Vs_slope: int or float,
                 Vs_base: int or float,
                 damp_ratio: float,
                 ref_strain: float,
                 soil_model: str = "linear_elastic",
                 SI_units: bool = True,
                 lite: bool = False):
        super().__init__()
        self.k_y = k_y
        self.a_in = a_in
        self.dt = dt
        self.height = height
        self.Vs_slope = Vs_slope
        self.Vs_base = Vs_base
        self.damp_ratio = damp_ratio
        self.ref_strain = ref_strain
        self.SI_units = SI_units
        self.soil_model = soil_model
        self.lite = lite

        self.npts = len(self.base_acc)
        self.g = G_EARTH*((not self.SI_units)*MtoFT)
        self.unit_weight = 20.0*((not self.SI_units)*KNM3toPCF)



        self.avgacc = np.zeros(self.npts)  #
        self.s = np.zeros(self.npts)  #
        self.sdot = np.zeros(self.npts)  #
        self.u = np.zeros(self.npts)  #
        self.udot = np.zeros(self.npts)  #
        self.udotdot = np.zeros(self.npts)  #

        self.acc2 = None
        self.acc1 = None
        self.rho = None
        self.scale_factor = None



    def run_sliding_analysis(self,ca):




        # copy ca into disp and mu
        # mu AND disp RELATED TO CRITICAL ACCELERATION. LENGTH > 1 IF CRITICAL ACCELERATION VARIES WITH DISPLACEMENT
        self.disp = ca[0]#[row[0] for row in ca]
        self.mu = ca[1]#[row[1] for row in ca]

        self.nmu = len(ca)  # LENGTH OF mu TABLE

          # NUMBER OF POINTS IN GROUND MOTION


        self.deltacc = 0.0
        # u1, udot, udotdot1 GROUND DISP, VELOCITY, ACCELERATION RESPECTIVELY
        self._u_prev = 0.0
        self._udot_prev = 0.0
        self._udotdot_prev = 0.0

        self.acc1 = 0.0
        self.acc2 = 0.0
        self.mx = 0.0
        self.mx1 = 0.0
        self.mmax = 0.0
        self.gameff1 = 0.0
        # self.n = 100.0
        # self.o = 100.0

        self.rho = self.unit_weight / self.g  # DENSITY

        self.dampf = 55.016 * (self.Vs_base / self.Vs_slope) ** -0.9904 / 100.0
        if self.dampf > 0.2:
            self.dampf = 0.2
        self.dampf = 0.2

        # self.scal *= -1.0

        # for each mode calculate constants.py for Slammer algorithm

        self.beta = 0.25
        self.gamma = 0.5
        self.Mtot = self.rho * self.height
        self.slide = True
        self.qq = 1

        self.omega = math.pi * self.Vs_slope / (2.0 * self.height)
        # L AND M CONSTANTS FROM RATHJE 1999?
        self.L = -2.0 * self.rho * self.height / math.pi * math.cos(math.pi)
        self.M = self.rho * self.height / 2.0

        self.n = 100.0
        self.o = 100.0
        self.gamref = refstrain_p
        self.damp = self.damp1 + self.dampf

        # loop for time steps in time histories

        # for equivalent linear
        if self.eqvlnr:
            self.equivalent_linear()

        # self.omega = math.pi * self.vs / (2.0 * self.height)

        # calculate final dynamic response using original prop's for LE analysis and EQL properties for EQL analysis
        for j in range(1, self.npts + 1):
            self.j = j
            self.d_setupstate()
            self.d_response()

        self.slide = False
        self.time = 0.0

        # self.find_kmax()

        # self._kmax = self.mmax
        # self._vs = self.vs
        # self._damp = self.damp
        # self._dampf = self.dampf
        # self._omega = self.omega

        # calculate decoupled displacements
        for j in range(1, self.npts + 1):
            self.d_sliding(j)
            # self.store(abs(self.s[j - 1]))
            self.residual_mu()

        # self.end(abs(self.s[self.npts - 1]))
        return abs(self.s[self.npts - 1])

    def d_setupstate(self):
        pass

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

    def eq_property(self):
        gameff2 = abs(self.gameff1) * 100.0
        vs2 = self.vs1 / math.sqrt(1.0 + (gameff2 / self.gamref))
        com1 = 1.0 / (1.0 + gameff2 / self.gamref)
        com2 = pow(com1, 0.1)

        self.damps = 0.0

        if not self.eqvlnr:
            self.dampf = 0.0
        else:
            self.dampf = 55.016 * pow((self.Vs_base / vs2), -0.9904)
            if self.dampf > 20.0:
                self.dampf = 20.0

        self.damps = 0.62 * com2 * (100.0 / math.pi * (4.0 * ((gameff2 - self.gamref * math.log((self.gamref + gameff2) / self.gamref)) / (gameff2 * gameff2 / (gameff2 + self.gamref))) - 2.0)) + 1.0
        damp2 = self.dampf + self.damps

        G1 = (self.unit_weight / self.g) * self.Vs_slope * self.Vs_slope
        G2 = (self.unit_weight / self.g) * vs2 * vs2

        l = (G1 - G2) / G1
        m = ((self.damps_prev - self.damps) / self.damps_prev)

        self.n = abs(l) * 100.0
        self.o = abs(m) * 100.0

        self.Vs_slope = vs2

        self.damps_prev = self.damps
        self.damp = damp2 * 0.01
        self.dampf = self.dampf * 0.01

    def residual_mu(self):
        if self.nmu > 1:
            if not self.slide and (abs(self.s[self.j - 1]) >= self.disp[self.qq - 1]):
                if self.qq <= (self.nmu - 1):
                    self.qq += 1



    # calculate Kmax
    def find_kmax(self):
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
        omega = math.pi * self.Vs_slope / (2.0 * self.height)

        khat = (omega * omega) + 2.0 * self.damp * omega * self.gamma / (self.beta * self.dt) + 1.0 / (self.beta * (self.dt * self.dt))
        a = 1.0 / (self.beta * self.dt) + 2.0 * self.damp * omega * self.gamma / self.beta
        b = 1.0 / (2.0 * self.beta) + self.dt * 2.0 * self.damp * omega * (self.gamma / (2.0 * self.beta) - 1.0)

        #a_in_prev
        #a_in_curr
        self.acc1 = self.base_acc[self.j - 2] * self.g * self.scale_factor
        self.acc2 = self.base_acc[self.j - 1] * self.g * self.scale_factor

        if not self.slide:
            self.s[self.j - 1] = self.s[self.j - 2]

        deltp = - self.L / self.M * (self.acc2 - self.acc1) + a * self._udot_prev + b * self._udotdot_prev
        deltu = deltp / khat
        deltudot = self.gamma / (self.beta * self.dt) * deltu - self.gamma / self.beta * self._udot_prev + self.dt * (
                    1.0 - self.gamma / (2.0 * self.beta)) * self._udotdot_prev
        deltudotdot = 1.0 / (self.beta * (self.dt * self.dt)) * deltu - 1.0 / (
                    self.beta * self.dt) * self._udot_prev - 0.5 / self.beta * self._udotdot_prev
        u2 = self._u_prev + deltu
        udot2 = self._udot_prev + deltudot
        udotdot2 = self._udotdot_prev + deltudotdot

        # if self.j == 1:
        #     deltp = - self.L / self.M * (self.acc2 - self.acc1)
        #     deltu = deltp / khat
        #     deltudot = self.gamma / (self.beta * self.dt) * deltu
        #     u2 = deltu
        #     udot2 = deltudot
        #     udotdot2 = - (self.L / self.M) * self.acc2 - 2.0 * self.damp * omega * udot2 - (omega * omega) * u2
        # else:
        #     deltp = - self.L / self.M * (self.acc2 - self.acc1) + a * self._udot_prev + b * self._udotdot_prev
        #     deltu = deltp / khat
        #     deltudot = self.gamma / (self.beta * self.dt) * deltu - self.gamma / self.beta * self._udot_prev + self.dt * (1.0 - self.gamma / (2.0 * self.beta)) * self._udotdot_prev
        #     deltudotdot = 1.0 / (self.beta * (self.dt * self.dt)) * deltu - 1.0 / (self.beta * self.dt) * self._udot_prev - 0.5 / self.beta * self._udotdot_prev
        #     u2 = self._u_prev + deltu
        #     udot2 = self._udot_prev + deltudot
        #     udotdot2 = self._udotdot_prev + deltudotdot

        self.avgacc[self.j - 1] = self.acc2
        self.u[self.j - 1] = u2
        self.udot[self.j - 1] = udot2
        self.udotdot[self.j - 1] = udotdot2
        self.avgacc[self.j - 1] = self.avgacc[self.j - 1] + self.L / self.Mtot * self.udotdot[self.j - 1]



    def equivalent_linear(self):
        t = 0

        while self.n > 5.0 or self.o > 5.0:
            for j in range(1, self.npts + 1):
                self.j = j
                self.d_setupstate()
                self.d_response()

            gamma_max = max(abs(self.u))
            self.gameff1 = 0.65 * 1.57 * gamma_max / self.height


            self.eq_property()



if __name__ == "__main__":
    histories = slam.sample_ground_motions()
    ky = 0.15
    motion = histories["Chi-Chi_1999_TCU068-090"]
    dt = motion[0][1] - motion[0][0]

    da = slam.Decoupled()
    out = da.run_sliding_analysis(ain_p=motion[1] / 9.80665,
                                  uwgt_p=20.0,
                                  height_p=50.0,
                                  vs_p=600.0,
                                  damp1_p=.05,
                                  refstrain_p=0.05,
                                  dt_p=dt,
                                  scal_p=-1.0,
                                  g_p=9.80665,
                                  vr_p=600.0,
                                  ca=[[1], [ky]],
                                  dv3_p=True)

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