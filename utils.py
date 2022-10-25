import numpy as np

# Optical Admittance of Free Space
# Y = (epsilon_0 / mu_0)^(1/2)
Y = 2.6544e-3 # 2.27

def make_interpolator(keys, values):
    '''
    Returns a function that interpolates between the given keys and values.
    
    Parameters:
    keys (list): list of keys to interpolate between
    values (list): list of values to interpolate between
    
    '''
    return lambda x: np.interp(x, keys, values)
