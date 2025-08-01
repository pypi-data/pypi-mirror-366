import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from astropy import units as u
from scipy.stats import ks_2samp
import os
import rebound

def get_runtime_data(base_path, n_runs, simarchive_name):
    data = []

    for i in range(n_runs):
        sim_id = i + 1
        simarchive_dir = f"{base_path}{sim_id}/{simarchive_name}{sim_id}"

        if not os.path.exists(simarchive_dir):
            print(f"Path does not exist: {simarchive_dir}")
            continue

        sa = rebound.Simulationarchive(simarchive_dir)

        sim_first = sa[0]
        E0 = sim_first.energy()
        last_tp = sa[-1].t

        for j in range(int(last_tp / 1e5)):
            sim = sa[j]
            t = sim.t
            N = sim.N
            wt = sim.walltime
            error = abs((sim.energy() - E0) / E0)

            data.append({
                "simulation_id": sim_id,
                "time": t,
                "relative_energy_error": error,
                "N_bodies": N,
                "walltime": wt,
            })

    df = pd.DataFrame(data)
    return df


def get_particle_params_at_time(base_path, runs, simarchive_name, time):
    """
    Extracts planetary parameters from simulation archives.

    Parameters:
    - base_path (str): Base path for simulation directories.
    - runs (list): List of run indices.

    Returns:
    - List of pandas DataFrames, each containing columns: ['semi', 'mass', 'radius', 'ecc', 'hash']
    """
    dataframes = []  # List to store DataFrames

    for i in runs:
        simarchive_dir = base_path +f"{i+1}"+"/"+simarchive_name+f"{i+1}" #sim archive directory 
        sa = rebound.Simulationarchive(simarchive_dir)
        snapshot = int(time/1e5) + 1
        sim_f = sa[snapshot] # Final snapshot
        n_bodies = sim_f.N - 3  # Exclude Sun, Jupiter, Saturn
        sim_id = i

    
        # Collect data for this run
        planet_data = {"semi": [], "mass": [], "radius": [], "ecc": [], "hash": [], "inc":[]}

        for j in range(n_bodies):
            a = sim_f.particles[j+1].a
            m = sim_f.particles[j+1].m
            r = sim_f.particles[j+1].r
            e = sim_f.particles[j+1].e
            h = sim_f.particles[j+1].hash.value  
            inc = sim_f.particles[j+1].inc

            if 0 <= a < 100:  # Filter valid semi-major axes
                planet_data["semi"].append(a)
                planet_data["mass"].append(m)
                planet_data["radius"].append(r)
                planet_data["ecc"].append(e)
                planet_data["hash"].append(h)
                planet_data["inc"].append(inc)

        # Convert to DataFrame and store
        df = pd.DataFrame(planet_data)
        df['sim_id'] = i
        dataframes.append(df)

    return dataframes  # List of DataFrames


def read_dbct_output(filename, total_cmf, boundary, percentage):
    df = pd.DataFrame(columns=['hash', 'mass', 'cmf'])

    data = np.loadtxt(filename)
    df['hash'] = data[:,0]
    df['mass'] = data[:,1]
    df['cmf'] = data[:,2]
    df['tot_disk_cmf'] = total_cmf
    df['boundary'] = boundary
    df['percentage'] = percentage

    return df



def extract_data_outfile_full(file_path):
    """
    Extracts collision time, types, and t versus number of bodies in simulation from the output file.
    Returns one panda's dataframe with everything!
    """
    df = pd.DataFrame(columns=['time', 'hash_t', 'Mt', 'hash_p', 'Mp',
                                'Mp/Mt', 'Mlr/Mt', 'Mlr/Mtot', 'b/Rt', 'Vimp/Vesc', 'Q/Q*', 'type'])
    index = 0

    with open(file_path, 'r') as file:
            for line in file:
                # Check if the line contains the desired phrase
                if "TIME OF COLLISION:" in line:
                    # Extract the value after "TIME OF COLLISION:"
                    df.loc[index, 'time'] = float(line.split(":")[1].strip())
                
                if "Target hash, mass =" in line:
                    hash_mass_t = line.split("=")[1].strip()
                    df.loc[index, 'hash_t'], df.loc[index, 'Mt'] = hash_mass_t.split()
                    
                if "Projectile hash, mass =" in line:
                    hash_mass_p = line.split("=")[1].strip()
                    df.loc[index, 'hash_p'], df.loc[index, 'Mp'] = hash_mass_p.split()
                    
                if "Mp/Mt:" in line:
                    df.loc[index, 'Mp/Mt'] = float(line.split(":")[1].strip())
                
                if "Mlr/Mt:" in line:
                    df.loc[index, 'Mlr/Mt'] = float(line.split(":")[1].strip())
                
                if "Mlr/Mtot:" in line:
                    df.loc[index, 'Mlr/Mtot'] = float(line.split(":")[1].strip())
                
                if "b/Rtarg:" in line:
                    df.loc[index, 'b/Rt'] = float(line.split(":")[1].strip())
                
                if "Vimp/Vesc:" in line:
                    df.loc[index, 'Vimp/Vesc'] = float(line.split(":")[1].strip())
                
                if "Q/ Qstar:" in line:
                    df.loc[index, 'Q/Q*'] = float(line.split(":")[1].strip())
                
                if "COLLISION TYPE:" in line:
                    df.loc[index, 'type'] = str(line.split(":")[1].strip())
                    index += 1
    return df




#This function reads .out files, and extracts collision times, collision types, and number of bodies versus time
def extract_data_impact(file_path):
    """
    Extracts collision time, types, and t versus number of bodies in simulation from the output file.
    """
    vi_vesc = []
    b_bcrit = []
    
    # Open and read the file
    with open(file_path, 'r') as file:
        for line in file:
            # Check if the line contains the desired phrase
            if "Vimp/Vesc:" in line:
                # Extract the value after "TIME OF COLLISION:"
                vi_vesc_value = float(line.split(":")[1].strip())
                vi_vesc.append(vi_vesc_value)
            
            if "b/Rtarg:" in line:
                # Extract the value after "COLLISION TYPE:"
                b_bcrit_value = float(line.split(":")[1].strip())
                b_bcrit.append(b_bcrit_value)
                

    vi_vesc = np.array(vi_vesc)
    b_bcrit = np.array(b_bcrit)
    
    
    return vi_vesc, b_bcrit



#function to plot v versus v
def plot_b_v(b, v, type):
    plt.clf()
    shape = np.zeros(len(type), dtype=object)
    color = np.zeros(len(type), dtype=object)
    
    for i in range(len(type)):
        if type[i] == 'EFFECTIVELY MERGED':
            shape[i] = 'D'
            color[i] = 'blue'
        
        elif type[i] == 'SIMPLY MERGED':
            shape[i] = 'D'
            color[i] = 'red'
        
        elif type[i] == 'PARTIAL ACCRETION':
            shape[i] = 'o'
            color[i] = 'black'
        
        elif type[i] == 'PARTIAL EROSION':
            shape[i] = '^'
            color[i] = 'grey'
    
        elif type[i] == 'SUPER-CATASTROPHIC':
            shape[i] = '^'
            color[i] = 'magenta'
            
        elif type[i] == 'GRAZE AND MERGE':
            shape[i] = 'o'
            color[i] = 'green'
        
        elif type[i] == 'ELASTIC BOUNCE':
            shape[i] = '*'
            color[i] = 'brown'
            
        elif type[i] == 'HIT AND RUN':
            shape[i] = '^'
            color[i] = 'orange'
            
        else:
            shape[i] = '*'
            color[i] = 'cyan'
            
    plt.figure(figsize=(10,6))

    # Track the types already used in the legend
    used_labels = set()

    for i in range(len(type)):
        label = type[i] if type[i] not in used_labels else None  # Only add label if it hasn't been used
        if label:
            used_labels.add(type[i])  # Add the label to the set

        plt.scatter(
        b[i], v[i], 
        label=label,
        marker=shape[i], 
        color=color[i]
        )
    plt.yscale('log')
    plt.xlabel('b/R_target')
    plt.ylabel('v/v_esc')
    plt.legend(loc='upper left')  # Show legend if needed

    plt.show()
    
    

#Function to make CDF
def make_cdf(data):
    data_sorted = np.sort(data)
    cdf = np.arange(1, len(data_sorted) + 1) / len(data_sorted)
    return data_sorted, cdf
    


def perform_ks_test(data1, data2, alpha=0.05):
    """
    Perform a Kolmogorov-Smirnov (K-S) test on two datasets.

    Parameters:
        data1 (array-like): First dataset.
        data2 (array-like): Second dataset.
        alpha (float): Significance level for the test. Default is 0.05.

    Returns:
        dict: A dictionary containing the test statistic, p-value, 
              and a conclusion about the null hypothesis.
    """
    # Perform the K-S test
    statistic, p_value = ks_2samp(data1, data2)
    
    # Interpretation of the result
    result = {
        "statistic": statistic,
        "p_value": p_value,
        "conclusion": "Reject H0: The datasets are significantly different."
                     if p_value < alpha else
                     "Fail to reject H0: No significant difference in the datasets."
    }
    return result
