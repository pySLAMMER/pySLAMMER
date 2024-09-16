import numpy as np
import pyslammer.constants as constants
import scipy.integrate as spint
import matplotlib.pyplot as plt
from pyslammer.rigid_block import RigidBlock


class Decoupled(RigidBlock):

    def __init__(self,
                 gnd_motion: np.ndarray=[],
                 name: str='',
                 height: float=0.0,
                 vs_slope: float=0.0,
                 vs_base: float=0.0,
                 damp_ratio: float=0.0,
                 ref_strain: float=0.0,
                 scale_factor: float = 1.0,
                 soil_model: str = "linear_elastic",
                 si_units: bool = True,
                 lite: bool = False):
        super().__init__(gnd_motion, name)
        self.height = height
        self.vs_slope = vs_slope
        self.vs_base = vs_base
        self.damp_ratio = damp_ratio
        self.ref_strain = ref_strain
        self.scale_factor = scale_factor
        self.soil_model = soil_model
        self.SI_units = si_units
        self.lite = lite

        self.g = constants.G_EARTH*(si_units + (not si_units)*constants.M_TO_FT)
        self.unit_weight = 20.0*(si_units + (not si_units)*constants.KNM3_TO_LBFT3)
        self.density = self.unit_weight / self.g  # DENSITY
        self.mass = self.unit_weight * height / self.g
        self.L1 = -2.0 * self.mass / np.pi * np.cos(np.pi)
        self.M1 = self.mass / 2.0
        self.max_shear_mod = self.density * vs_slope**2

        self.HEA = np.zeros(self._npts)
        self.block_disp = np.zeros(self._npts)
        self.block_vel = np.zeros(self._npts)
        self.x_resp = []
        self.v_resp = []
        self.a_resp = []

        # special variables that change during the analysis
        self._slide = False
        self._vs_slope = vs_slope
        self._omega = np.pi * vs_slope / (2.0 * height)
        self._damp_imp = impedance_damping(vs_base, vs_slope)
        self._damp_tot = damp_ratio + self._damp_imp

    def decoupled_analysis(self):

        pass

    def run_sliding_analysis(self): #TODO: add ca to inputs

        if self.soil_model == "equivalent_linear":
            self.equivalent_linear()

        for i in range(1, self._npts + 1):
            self.dynamic_response(i)

        # calculate decoupled displacements
        for i in range(1, self._npts + 1):
            self.sliding(i)

        self.total_disp =  self.block_disp[-1]
        return self.total_disp

    def sliding(self, i): #TODO: refactor
        # variables for the previous and current time steps
        # prev and curr are equal for the first time step
        #TODO: consider just starting at i=2 and eliminating the logical statement in prev
        # alternatively, removing logical and letting it use the last value of the array...
        prev = i - 2 + (i == 1)
        curr = i - 1

        # yield_acc = self.k_y(self.block_disp[prev]) * self.g             ASSUME self.k_y
        excess_acc = yield_acc - self.HEA[prev]
        delta_hea = self.HEA[curr] - self.HEA[prev]

        # if k_y_testing:
        #     if i%500 == 0:
        #         print(f"disp: {self.block_disp[prev]}, ky: {self.k_y(self.block_disp[prev])}")

        if not self._slide:
            self.block_vel[curr] = 0
            self.block_disp[curr] = self.block_disp[prev]
            if self.HEA[curr] > yield_acc:
                self._slide = True
        else:
            self.block_vel[curr] = (self.block_vel[prev]
                                    + (excess_acc - 0.5 * delta_hea) * self.dt)
            self.block_disp[curr] = (self.block_disp[prev]
                                     - self.block_vel[prev] * self.dt
                                     - 0.5 * (excess_acc + delta_hea / 6.0) * self.dt**2)
            if self.block_vel[curr] >= 0.0:
                self._slide = False

    def dynamic_response(self,i):
        prev = i - 2 + (i == 1)
        curr = i - 1
        # Newmark Beta Method constants
        beta = 0.25 #TODO: move outside of function (up to delta_a_in)
        gamma = 0.5 #TODO: move constants outside of function

        self._omega = np.pi * self._vs_slope / (2.0 * self.height)

        k_eff = (self._omega ** 2
                 + 2.0 * self._damp_tot * self._omega * gamma / (beta * self.dt)
                 + 1.0 / (beta * self.dt**2))
        a = (1.0 / (beta * self.dt)
             + 2.0 * self._damp_tot * self._omega * gamma / beta)
        b = (1.0 / (2.0 * beta)
             + 2.0 * self.dt * self._damp_tot * self._omega * (gamma / (2.0 * beta) - 1.0))
        for i in range(self._npts):
            if i == 0:
                self.x_resp.append(0.0)
                self.v_resp.append(0.0)
                self.a_resp.append(0.0)               
            else:
                delta_a_in = self.gnd_acc[i] - self.gnd_acc[i-1]
                delta_force = (- self.L1 / self.M1 * delta_a_in * self.g * self.scale_factor
                            + a * self.v_resp[i-1]
                            + b * self.a_resp[i-1])
                delta_x_resp = delta_force / k_eff
                delta_v_resp = (gamma / (beta * self.dt) * delta_x_resp
                                - gamma / beta * self.v_resp[i-1]
                                + self.dt * (1.0 - gamma / (2.0 * beta)) * self.a_resp[i-1])
                delta_a_resp = (1.0 / (beta * (self.dt * self.dt)) * delta_x_resp
                                - 1.0 / (beta * self.dt) * self.v_resp[i-1]
                                - 0.5 / beta * self.a_resp[i-1])
                self.x_resp.append(self.x_resp[i-1] + delta_x_resp)
                self.v_resp.append(self.v_resp[i-1] + delta_v_resp)
                self.a_resp.append(self.a_resp[i-1] + delta_a_resp)

        self.HEA[i] = self.gnd_acc[i]*self.g + self.L1 / self.mass * self.a_resp[i]



    def equivalent_linear(self):
        tol = 0.05 #TODO: move constants outside of function
        max_iterations = 100 #TODO: move constants outside of function
        rel_delta_mod = 1
        rel_delta_damp = 1
        shear_mod = self.max_shear_mod
        damp_ratio = self.damp_ratio
        count = 0
        while rel_delta_damp > tol or rel_delta_mod > tol: #TODO: confirm whether number of iterations and order of operations matches SLAMMER
            for i in range(1, self._npts + 1):
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


            self._vs_slope = np.sqrt(new_mod / self.density)
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
k_y_testing = False

def some_ky_func(disp):
    initial = 0.15
    minimum = 0.05
    factor = 0.005
    exponent = -1.5
    value = max(factor*(disp+minimum)**exponent + 0.4*disp, minimum)
    return min(initial,value)

# if __name__ == "__main__":
#     if mrd_testing:
#         strains = np.linspace(0.0001, 0.1, 1000)
#         mod_reduction = []
#         damping = []
#         for strain in strains:
#             mod_reduction.append(strain_mod_update(strain, 0.0005))
#             damping.append(strain_damp_update(strain_mod_update(strain, 0.0005), strain, 0.0005))
#         darendelli = [mod_damp_testing(strain, 0.0005) for strain in strains]
#         plt.close("all")
#         # plt.plot(mod_reduction, damping)
#         plt.semilogx(strains, mod_reduction)
#         plt.semilogx(strains, damping)
#         plt.show()
#     else:
#         histories = slam.sample_ground_motions()
#         ky_const = 0.15
#         ky_interp = ([0.2, 0.3, 0.4, 0.5], [0.15, 0.14, 0.13, 0.12])
#         ky_func = some_ky_func
#         motion = histories["Chi-Chi_1999_TCU068-090"]
#         t_step = motion[0][1] - motion[0][0]
#         input_acc = motion[1] / 9.80665

#         da = slam.Decoupled(k_y=ky_const,
#                             a_in=input_acc,
#                             dt=t_step,
#                             height=50.0,
#                             vs_slope=600.0,
#                             vs_base=600.0,
#                             damp_ratio=0.05,
#                             ref_strain=0.0005,
#                             scale_factor=1.0,
#                             soil_model="equivalent_linear",
#                             si_units=True,
#                             lite=False)

#         da.run_sliding_analysis()

#         print(da.block_disp[-1]*100)