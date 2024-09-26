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

        self.HEA = []
        self.x_resp = []
        self.v_resp = []
        self.a_resp = []

        # special variables that change during the analysis
        self._slide = False
        self._vs_slope = vs_slope
        self._omega = np.pi * vs_slope / (2.0 * height)
        self._damp_imp = self.impedance_damping(vs_base, vs_slope)
        self._damp_tot = damp_ratio + self._damp_imp

    def impedance_damping(vs_base, vs_slope):
        # Adjust for base impedance. include_impedance_damping()?
        vs_ratio = vs_base / vs_slope
        damp_imp = 0.55016 * vs_ratio ** -0.9904 #TODO: move constants outside of function
        damp_imp = min(damp_imp, 0.2) #TODO: move constants outside of function
        return damp_imp

    def dynamic_response(self,i):
        # Calculates HEA
        self._omega = np.pi * self._vs_slope / (2.0 * self.height)
        k_eff = (self._omega ** 2
                + 2.0 * self._damp_tot * self._omega * constants.GAMMA / (constants.BETA * self.dt)
                + 1.0 / (constants.BETA * self.dt**2))
        a = (1.0 / (constants.BETA * self.dt)
            + 2.0 * self._damp_tot * self._omega * constants.GAMMA / constants.BETA)
        b = (1.0 / (2.0 * constants.BETA)
            + 2.0 * self.dt * self._damp_tot * self._omega * (constants.GAMMA / (2.0 * constants.BETA) - 1.0))      
        
        for i in range(len(self._npts)):
            d_gnd_acc = self.gnd_acc[i] - self.gnd_acc[i-1]
            df = (- self.L1 / self.M1 * d_gnd_acc * self.g * self.scale_factor
                        + a * self.v_resp[-1]
                        + b * self.a_resp[-1])
            d_disp_resp = df / k_eff
            d_vel_resp = (constants.GAMMA / (constants.BETA * self.dt) * d_disp_resp
                        - constants.GAMMA / constants.BETA * self.v_resp[-1]
                        + self.dt * (1.0 - constants.GAMMA / (2.0 * constants.BETA)) * self.a_resp[-1])
            d_acc_resp = (1.0 / (constants.BETA * (self.dt * self.dt)) * d_disp_resp
                        - 1.0 / (constants.BETA * self.dt) * self.v_resp[-1]
                        - 0.5 / constants.BETA * self.a_resp[-1])

            self.x_resp.append(self.x_resp[-1] + d_disp_resp)
            self.v_resp.append(self.v_resp[-1] + d_vel_resp)
            self.a_resp.append(self.a_resp[-1] + d_acc_resp)

            self.HEA.append(self.gnd_acc[i]*self.g + self.L1 / self.mass * self.a_resp[-1])