import numpy as np
import RigidBlock as rb

height = np.arange(0, 10, 0.1)
damping_ratio = 0.05
shear_velocity = 1
mass_dist = np.arange(0, 10, 0.1)

angular_freq = (np.pi*shear_velocity) / (2*height[-1])
mode_shape = np.cos((np.pi*height) / (2*height[-1]))

accel_dist = np.trapz(mode_shape * mass_dist)