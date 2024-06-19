#=====================
#DEFINE DIRECTORIES
#=====================
import experiment_params as params
import os
stimuli_dir = params.stimuli_dir
data_dir = params.data_dir
table_dir = params.table_dir
os.makedirs(table_dir, exist_ok=True)

#=====================
#VARIABLES
#=====================
import numpy as np
import itertools
# IV 1: DURATION
# Generate a linearly spaced array
unit_dur_cond = np.linspace(params.min_unit_dur, params.max_unit_dur, params.n_unit_dur_cond)
unit_dur_list = unit_dur_cond.tolist()

# IV 2: PROPORTION OF THE REPEATING TONES
rep_percentage_cond = np.linspace(params.min_rep_percentage, params.max_rep_percentage, params.n_rep_percentage_cond)  
rep_percentage_list = rep_percentage_cond.tolist()

# Generate all combinations of repdur and percentage
# in one block, there should be 60 examples of non zero percentages, and 360 examples of the zero percentage
combinations = list(itertools.product(unit_dur_list, rep_percentage_list))

#=====================
#CREATE THE DATA FRAME
#=====================
import pandas as pd
import time
from data_frame_functions import generate_baseline_table
from stim_production_functions import gencloudcoherence
from scipy.io.wavfile import write
from scipy import signal
import pickle

# within a block, the number of 0 percent condition is 27, for each duration
# Again, for each duration, there are basically two crude categories: 
# stimulus absent(percentage_zero) and stimulus present(the remainin 9 levels)
# for each stimulus present level, there are corresponding stimulus absent trials. 
# nTrial_0.111 = 3, corresponding to that nTrial_0 = 3
# nTrial_0.222 = 3, corresponding to that nTrial_0 = 3
# nTrial_0.333 = 3, corresponding to that nTrial_0 = 3
# nTrial_0.444 = 3, corresponding to that nTrial_0 = 3
# nTrial_0.556 = 3, corresponding to that nTrial_0 = 3
# nTrial_0.667 = 3, corresponding to that nTrial_0 = 3
# nTrial_0.778 = 3, corresponding to that nTrial_0 = 3
# nTrial_0.889 = 3, corresponding to that nTrial_0 = 3
# nTrial_1 = 3,     corresponding to that nTrial_0 = 3
# this means that the number of percentage zero trials should be 9*3, the number of other level trials shoudl be 3
# I HOPE THIS IS CLEAR ENOUGH!!!
n_percentage_zero = 27
n_rest = 3

for iblock in range(params.nblocks):

    block_id = iblock + 1

    # specify specific directories
    # store the sound files in .wav format
    specific_stimuli_dir = os.path.join(stimuli_dir, f"block{block_id}")
    os.makedirs(specific_stimuli_dir, exist_ok=True)

    # store sound signals 
    signal_dir = os.path.join(data_dir, f"block{block_id}", 'signal_data')
    os.makedirs(signal_dir, exist_ok=True)

    # first, generate bunch of lists
    table_values, ntrials = generate_baseline_table(unit_dur_list, rep_percentage_list, n_percentage_zero, n_rest)

    # Create a DataFrame from the list
    table_values = pd.DataFrame(table_values, columns=['unitdur', 'percentage', 'stim_code', 'expected_response'])
    
    # add other things to the data frame
    table_values.insert(0, 'block', block_id*np.ones(ntrials, dtype='int')) 
    table_values.insert(len(table_values.columns), 'iti', params.iti*np.ones(ntrials, dtype='int')) 

    # Create an array of ntrials random seed values
    # I will use them when i create tone clouda
    rng = np.random.default_rng(int(time.time()))
    seed_values = rng.uniform(low = 0, high = 2**32-1, size = ntrials)
    table_values.insert(len(table_values.columns), 'seed', seed_values)

    #=====================
    #CREATE SOUND SIGNAL AND MAKE THE DATA FRAME LARGER AND LARGER
    #=====================
    # there are zeropads at the beginning and at the end of the signal to prevent bursts
    # duration of the zeropads are: 0.2 (at the beginning) and 0.2 (at the end)
    signal = []

    # Iterate through the rows of experiment_table
    for index, row in table_values.iterrows():
        # Extract the relevant parameters from the current row
        unitdur = row['unitdur']
        percentage = row['percentage']
        seedval = row['seed']
        
        # create change_dict for the current row
        change_dict = {'unitdur' : unitdur, 'percentage' : percentage, 'seed': int(seedval)}

        # Generate the sound stimulus based on the parameters
        y, sP = gencloudcoherence(change_dict=change_dict)

        # Create the output file name
        stim_name = 'index_' + str(index) + '_unitdur_' + str(unitdur) + '_percentage_' + str(percentage) + '.wav'
        table_values.loc[index, 'stim_name'] = stim_name
        
        # Save the audio data to a file in the "stimuli" folder
        file_path = os.path.join(specific_stimuli_dir, stim_name)
        write(file_path, sP['fs'], y)

        # Extract values from sP dictionary and add as new columns to table_values
        for param_name, param_value in sP.items():
            table_values.loc[index, param_name] = param_value

        table_values.loc[index, 'signal_length'] = len(y)
        table_values.loc[index, 'stim_duration'] = len(y)/sP['fs']

        # Append the sound stimulus and parameters to the list as a tuple
        signal.append((y, sP.copy()))

    #=====================
    #ADD COUPLE OF THINGS TO THE GIANT DATA FRAME
    #=====================
    for index, row in table_values.iterrows():
        isi_value = row['stim_duration'] + row['iti']
        table_values.loc[index, 'max_isi'] = isi_value

    # save the data frame
    tsv_filename = 'block_' + str(block_id) + '_table.tsv'    
    table_path = os.path.join(table_dir, tsv_filename)
    table_values.to_csv(table_path, sep='\t', index=False)

    #=====================
    #SAVE THE SIGNAL VARIABLE
    #=====================
    # Save the signal variable as a pickle file
    signal_filename = 'block_' + str(block_id) + '_signal.pkl'
    signal_path = os.path.join(signal_dir, signal_filename)

    with open(signal_path, 'wb') as f:
        pickle.dump(signal, f)


# # Load the signal variable from the pickle file
# with open(signal_path, 'rb') as f:
#     loaded_signal = pickle.load(f)

