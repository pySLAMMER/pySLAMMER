import Utilities
import RigidBlock

while True:
    user_mode = input('(1) Normal Mode \n(2) Test Mode \n(3) Quit \nSelect a mode: \n')
    try:
        user_mode = int(user_mode)
    except ValueError:
        print('Enter a valid mode.')
    if user_mode == 3:
        break
    while True:
        if user_mode == 1:
            time_history = Utilities.csv_time_hist()
            if time_history is None:
                break
            else:
                pass
            while True:
                acc_crit = input('Enter critical acceleration (g): ')
                try:
                    acc_crit = float(acc_crit) * Utilities.G_EARTH
                    break
                except ValueError:
                    print('Enter a valid number.')
            method = input('(1) Jibson \n(2) Garcia-Rivas \nSelect a method: \n')
            try:
                method = int(method)
            except ValueError:
                print('Enter a valid method.')
            if method == 1:
                data = RigidBlock.downslope_analysis_jibson(time_history, acc_crit)
            elif method == 2:
                data = RigidBlock.downslope_analysis_dgr(time_history, acc_crit)
            else:
                pass
        elif user_mode == 2:
            time_history = Utilities.test_time_hist()
            while True:
                acc_crit = input('Enter critical acceleration (g): ')
                try:
                    acc_crit = float(acc_crit) * Utilities.G_EARTH
                    break
                except ValueError:
                    print('Enter a valid number.')
            method = input('(1) Jibson \n(2) Garcia-Rivas \nSelect a method: \n')
            try:
                method = int(method)
            except ValueError:
                print('Enter a valid method.')
            if method == 1:
                data = RigidBlock.downslope_analysis_jibson(time_history, acc_crit)
            elif method == 2:
                data = RigidBlock.downslope_analysis_dgr(time_history, acc_crit)
            else:
                pass
        exit = input('Continue in current mode? (y/n): ')
        if exit == 'y':
            pass
        else:
            break