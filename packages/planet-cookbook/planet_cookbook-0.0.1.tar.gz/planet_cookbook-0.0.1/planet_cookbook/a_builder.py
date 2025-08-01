#import rebound
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from astropy import units as u

# Define constants
AU = 1.496e+13 #cm
M_sun = 1.989e+33 #g

#A few useful functions
#Uniform random distribution
def rand_uniform(minimum, maximum):
    return np.random.uniform()*(maximum-minimum)+minimum

#Inverse CDF function
def inverse_cdf(alpha, N, r_min, r_max):
    #alpha is the exponent for the power-law distribution
    #N is number of samples
    #r_min is the minimum value of r
    #r_max is the maximum value of r

    # Generate uniform random numbers between 0 and 1
    u = np.random.uniform(0, 1, N)

    # Inverse transform sampling for r^-alpha distribution
    if alpha != 1:
        # For alpha != 1, use the inverse CDF derived for r^-alpha
        r_values = ((u * (r_max**(1 - alpha) - r_min**(1 - alpha)) + r_min**(1 - alpha))**(1 / (1 - alpha)))
    else:
        # Special case for alpha = 1, which corresponds to a logarithmic distribution
        r_values = r_min * (r_max / r_min) ** u
        
    return r_values

#Surface density function, Sigma = b * r^(power), finds b first using total mass
#inputs: R is where you want the local surface density, r_min and r_max are the edges of disk,
#power is as specified above, total_mass is total mass in the disk
def surface_density(R, r_min, r_max, power, total_mass):
    b = (total_mass)/(np.pi * (r_max**2 - r_min**2) * (r_max)**power)
    Sigma = b * R**(power)
    return Sigma


#Function to compute mass in disk with n steps, using the assigned semi major axis and mass of bodies
#delta_m - mass of each annulus when you divide your whole disk into n_steps
#m_sum - mass of each annulus when you start from a_min and keep adding delta_a
#delta_sigma - surface density of each annulus when you divide the disk into n_steps
def disk_mass_check(a, body_mass, body_n, n_steps, a_min, a_max):
    x = np.linspace(a_min, a_max, n_steps)
    delta_m = np.zeros(n_steps)
    delta_sigma = np.zeros(n_steps)
    m_sum = np.zeros(n_steps)
    
    # Calculate areas of each annulus
    areas = np.pi * (x[1:]**2 - x[:-1]**2)

    # Assign body mass to each annulus
    indices = np.digitize(a, x) - 1  # Get index of annulus for each body
    np.add.at(delta_m, indices, body_mass)
    
    # Calculate surface density
    delta_sigma[1:] = delta_m[1:] / areas
    m_sum = np.cumsum(delta_m)
    
    return delta_m, m_sum, delta_sigma









