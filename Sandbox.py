import RigidBlock
import Utilities
from pathlib import Path


user_csv = Utilities.test_time_hist(10, 0.05, write=True)
print('--------------------------------------------------')
print('Jibson Method: ')
jibson = RigidBlock.downslope_analysis_jibson(user_csv, 0.1)
print('Garcia-Rivas Method: ')
dgr = RigidBlock.downslope_analysis_dgr(user_csv, 0.1)
print('--------------------------------------------------')
#Utilities.write_output(dgr)