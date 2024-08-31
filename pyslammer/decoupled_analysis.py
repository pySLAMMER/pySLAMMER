# Decoupled Block Analysis
#TODO: add docstrings
#TODO: add inherited variable values
#TODO: add "testing" features?
import numpy as np

import pyslammer as slam
import matplotlib.pyplot as plt

from pyslammer.analysis import SlidingBlockAnalysis
from pyslammer.constants import *
import math

def mod_damp_testing(effective_strain, ref_strain):
    g_over_gmax = strain_mod_update(effective_strain, ref_strain)
    new_damp = strain_damp_update(g_over_gmax, effective_strain, ref_strain)
    return g_over_gmax, new_damp

def strain_mod_update(effective_strain, ref_strain):
    return 1 / (1 + (effective_strain / ref_strain) ** 1) #TODO: move constants outside of function


def strain_damp_update(g_over_gmax, shear_strain, ref_strain):
    m1 = 1/math.pi
    m2 = shear_strain
    m3 = ref_strain
    m4 = shear_strain + ref_strain
    m5 = m4/m3
    m6 = m2**2 / m4
    masing_damping = m1*(4 * (m2-m3*math.log(m5)) / m6 - 2)


    new_damp = 0.62 * g_over_gmax**0.1 * masing_damping + 0.01 #TODO: move constants outside of function

    if equivalent_linear_testing:
        print(f"g_over_gmax: {g_over_gmax}")
        print(f"masing_damping: {masing_damping}")
        print(f"new_damp: {new_damp}")

    return new_damp


def impedance_damping(vs_base, vs_slope):
    # Adjust for base impedance. include_impedance_damping()?
    vs_ratio = vs_base / vs_slope
    damp_imp = 0.55016 * vs_ratio ** -0.9904 #TODO: move constants outside of function
    damp_imp = min(damp_imp, 0.2) #TODO: move constants outside of function
    return damp_imp


class Decoupled(SlidingBlockAnalysis):
    # include allowed values for inputs, like soil_model
    def __init__(self,
                 k_y: float,  # TODO: or tuple[list[float], list[float]] or tuple[np.ndarray,np.ndarray] or callable(float),
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
        super().__init__()
        self.k_y = k_y
        self.a_in = a_in
        self.dt = dt
        self.height = height
        self.vs_slope = vs_slope
        self.vs_base = vs_base
        self.damp_ratio = damp_ratio
        self.ref_strain = ref_strain
        self.SI_units = si_units
        self.soil_model = soil_model
        self.lite = lite

        self.scale_factor = scale_factor

        self.npts = len(a_in)
        self.g = G_EARTH*(si_units + (not si_units)*MtoFT)
        self.unit_weight = 20.0*(si_units + (not si_units)*KNM3toPCF) #TODO: move constants outside of function
        self.rho = self.unit_weight / self.g  # DENSITY
        self.mass = self.unit_weight * height / self.g
        self.L1 = -2.0 * self.mass / math.pi * math.cos(math.pi)
        self.M1 = self.mass / 2.0
        self.max_shear_mod = self.rho * vs_slope**2

        self.HEA = np.zeros(self.npts)  #
        self.block_disp = np.zeros(self.npts)  #
        self.block_vel = np.zeros(self.npts)  #
        self.x_resp = np.zeros(self.npts)  #
        self.v_resp = np.zeros(self.npts)  #
        self.a_resp = np.zeros(self.npts)  #

        # special variables that change during the analysis
        self._slide = True
        self._vs_slope = vs_slope
        self._omega = math.pi * vs_slope / (2.0 * height)
        self._damp_imp = impedance_damping(vs_base, vs_slope)
        self._damp_tot = damp_ratio + self._damp_imp



    def run_sliding_analysis(self,ca=None): #TODO: add ca to inputs

        if self.soil_model == "equivalent_linear":
            self.equivalent_linear()

        for i in range(1, self.npts + 1):
            self.dynamic_response(i)

        self._slide = False

        # calculate decoupled displacements
        for i in range(1, self.npts + 1):
            self.d_sliding(i)
            self.residual_mu()

        return abs(self.block_disp[self.npts - 1])

    def d_sliding(self, j): #TODO: refactor
        # calculate decoupled displacements

        if j == 1:
            deltacc = self.HEA[j - 1]
        else:
            deltacc = self.HEA[j - 1] - self.HEA[j - 2]

        if j == 1:
            self.block_vel[j - 1] = 0
            self.block_disp[j - 1] = 0
        elif not self._slide:
            self.block_vel[j - 1] = 0
            self.block_disp[j - 1] = self.block_disp[j - 2]
        else:
            self.block_vel[j - 1] = self.block_vel[j - 2] + (self.k_y * self.g - self.HEA[j - 2]) * self.dt - 0.5 * deltacc * self.dt
            self.block_disp[j - 1] = self.block_disp[j - 2] - self.block_vel[j - 2] * self.dt - 0.5 * (self.k_y * self.g - self.HEA[j - 2]) * self.dt**2 + deltacc * self.dt**2 / 6.0

        if not self._slide:
            if self.HEA[j - 1] > self.k_y * self.g:
                self._slide = True
        else:
            if self.block_vel[j - 1] >= 0.0:
                self._slide = False

                if j == 1:
                    self.block_disp[j - 1] = 0
                else:
                    self.block_disp[j - 1] = self.block_disp[j - 2]

                self.block_vel[j - 1] = 0.0


    def residual_mu(self):
        #FIXME: update to use k_y as a function of displacement. not currently working
        # if self.nmu > 1:
        #     if not self._slide and (abs(self.block_disp[self.j - 1]) >= self.disp[self.qq - 1]):
        #         if self.qq <= (self.nmu - 1):
        #             self.qq += 1
        pass


    def dynamic_response(self,i):
        # Newmark Beta Method constants
        beta = 0.25 #TODO: move outside of function (up to delta_a_in)
        gamma = 0.5 #TODO: move constants outside of function

        self._omega = math.pi * self._vs_slope / (2.0 * self.height)

        k_eff = (self._omega ** 2
                 + 2.0 * self._damp_tot * self._omega * gamma / (beta * self.dt)
                 + 1.0 / (beta * self.dt**2))
        a = (1.0 / (beta * self.dt)
             + 2.0 * self._damp_tot * self._omega * gamma / beta)
        b = (1.0 / (2.0 * beta)
             + 2.0 * self.dt * self._damp_tot * self._omega * (gamma / (2.0 * beta) - 1.0))

        delta_a_in = self.a_in[i - 1] - self.a_in[i - 2]

        if not self._slide:#FIXME: needed?
            self.block_disp[i - 1] = self.block_disp[i - 2]

        delta_force = (- self.L1 / self.M1 * delta_a_in * self.g * self.scale_factor
                       + a * self.v_resp[i - 2]
                       + b * self.a_resp[i - 2])
        delta_x_resp = delta_force / k_eff
        delta_v_resp = (gamma / (beta * self.dt) * delta_x_resp
                    - gamma / beta * self.v_resp[i - 2]
                    + self.dt * (1.0 - gamma / (2.0 * beta)) * self.a_resp[i - 2])
        delta_a_resp = (1.0 / (beta * (self.dt * self.dt)) * delta_x_resp
                       - 1.0 / (beta * self.dt) * self.v_resp[i - 2]
                       - 0.5 / beta * self.a_resp[i - 2])

        self.x_resp[i - 1] = self.x_resp[i - 2] + delta_x_resp
        self.v_resp[i - 1] = self.v_resp[i - 2] + delta_v_resp
        self.a_resp[i - 1] = self.a_resp[i - 2] + delta_a_resp

        self.HEA[i - 1] = self.a_in[i - 1]*self.g + self.L1 / self.mass * self.a_resp[i - 1]



    def equivalent_linear(self):
        tol = 0.05 #TODO: move constants outside of function
        max_iterations = 100 #TODO: move constants outside of function
        rel_delta_mod = 1
        rel_delta_damp = 1
        shear_mod = self.max_shear_mod
        damp_ratio = self.damp_ratio
        count = 0
        while rel_delta_damp > tol or rel_delta_mod > tol: #TODO: confirm whether number of iterations and order of operations matches SLAMMER
            for i in range(1, self.npts + 1):
                self.dynamic_response(i)
            peak_disp = max(abs(self.x_resp))
            effective_strain = 0.65 * 1.57 * peak_disp / self.height #TODO: move constants outside of function
            g_over_gmax = strain_mod_update(effective_strain, self.ref_strain)
            new_mod = g_over_gmax * self.max_shear_mod
            new_damp = strain_damp_update(g_over_gmax, effective_strain, self.ref_strain)

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
                print("Warning: Maximum iterations reached. Equivalent linear procedure did not converge.")


mrd_testing = False
equivalent_linear_testing = False
if __name__ == "__main__":
    if mrd_testing:
        strains = np.linspace(0.0001, 0.1, 1000)
        mod_reduction = []
        damping = []
        for strain in strains:
            mod_reduction.append(strain_mod_update(strain, 0.0005))
            damping.append(strain_damp_update(strain_mod_update(strain, 0.0005), strain, 0.0005))
        darendelli = [mod_damp_testing(strain, 0.0005) for strain in strains]
        plt.close("all")
        # plt.plot(mod_reduction, damping)
        plt.semilogx(strains, mod_reduction)
        plt.semilogx(strains, damping)
        plt.show()
    else:
        histories = slam.sample_ground_motions()
        ky = 0.15
        motion = histories["Chi-Chi_1999_TCU068-090"]
        t_step = motion[0][1] - motion[0][0]
        input_acc = motion[1] / 9.80665

        da = slam.Decoupled(k_y=ky,
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
                            lite=False)

        da.run_sliding_analysis()

        print(da.block_disp[-1]*100)