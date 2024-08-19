import numpy as np
from Record import Record

G_EARTH = 9.80665 # Acceleration due to gravity (m/s^2).

class RigidBlock(Record):
    def __init__(self, gnd_motion: np.ndarray=[], name: str=''):
        super().__init__(gnd_motion, name)
        self.k_y = 0.0
        self.block_acc = []
        self.block_vel = []
        self.block_disp = []
        self.total_disp = 0.0

    def __str__(self):
        if self.dt == -1.0:
            info = ('Record: {}\n'.format(self.name))
        else:
            info = (
                    'Rigid Block Analysis\n'+
                    'Record  : {}\n'.format(self.name)+
                    'PGA     : {:.3f} g\n'.format(self.pga)+
                    'dt      : {:.3f} s\n'.format(self.dt)+
                    'k_y     : {:.3f} m/s^2\n'.format(self.k_y)+
                    'Disp    : {:.3f} m'.format(self.total_disp)
                )
        return info
    
    def downslope_jibson(self, k_y: float=None):
        """
        Perform downslope analysis using Jibson's 1993 method.

        Parameters:
        - k_y (float): Critical acceleration (g).
        """
        if self.dt == -1.0:
            return
        else:
            tol = 0.00001
            self.k_y = k_y * G_EARTH

        # [previous, current]
        acc = [0, 0]
        vel = [0, 0]
        pos = [0, 0]

        for i in range(len(self.gnd_acc)):
            gnd_acc_curr = self.gnd_acc[i]
            if vel[1] < tol:
                if abs(gnd_acc_curr) > self.k_y:
                    n = gnd_acc_curr / abs(gnd_acc_curr)
                else:
                    n = gnd_acc_curr / self.k_y
            else:
                n = 1
            acc[1] = gnd_acc_curr - n * self.k_y
            vel[1] = vel[0] + (self.dt / 2) * (acc[1] + acc[0])
            if vel[1] > 0:
                pos[1] = pos[0] + (self.dt / 2) * (vel[1] + vel[0])
            else:
                vel[1] = 0
                acc[1] = 0
            pos[0] = pos[1]
            vel[0] = vel[1]
            acc[0] = acc[1]
            self.block_disp.append(pos[1])
            self.block_vel.append(vel[1])
            self.block_acc.append(acc[1])
            self.total_disp = self.block_disp[-1]