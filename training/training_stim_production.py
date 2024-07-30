#=====================
#IMPORT IMPORTANT STUFF
#=====================
# defaults
import sys
default_path = '/Users/bastugb/Desktop/detection_experiment'
sys.path.append(default_path)

import os
import experiment_params as params
import numpy as np
import itertools
import pandas as pd
import time
from data_frame_functions import generate_baseline_table
from tone_cloud_production import gencloudcoherence
from scipy.io.wavfile import write
from scipy import signal
import pickle

#=====================
#DEFINE DIRECTORIES
#=====================
# when I switch to a new computer, just change the main_dir
main_dir = '/Users/bastugb/Desktop/detection_experiment/training'
stimuli_dir = main_dir + '/stimuli_training'
data_dir = main_dir + '/data_training'
table_dir = main_dir + '/tables_training'

# create the table directory to start with
os.makedirs(table_dir, exist_ok=True)

#=====================
#VARIABLES
#=====================
# IV 1: DURATION
# Generate a linearly spaced array
unit_dur_list = [0.4, 1.]

# IV 2: REPEATING PERCENTAGE OF THE TONES
rep_percentage_list = [0, 0.2, 0.7, 1.]


combinations = list(itertools.product(unit_dur_list, rep_percentage_list))

#=====================
#CREATE THE DATA FRAME
#=====================
n_percentage_zero = 3  # number of signal absent trials
n_rest = 1  # number of signal present trials
# their ratio is different in the detection experiment, but in the tapping experiment
# we keep the ratio the same

# store the sound files in .wav format
os.makedirs(stimuli_dir, exist_ok=True)

# store sound signals 
os.makedirs(data_dir, exist_ok=True)

# first, generate bunch of lists
table_values, ntrials = generate_baseline_table(unit_dur_list, rep_percentage_list, n_percentage_zero, n_rest)

# Create a DataFrame from the list
table_values = pd.DataFrame(table_values, columns=['unitdur', 'percentage', 'stim_code', 'expected_response'])

# add other things to the data frame
# first add block id and inter trial interval
block_id = 0
table_values.insert(0, 'block', block_id*np.ones(ntrials, dtype='int')) 
table_values.insert(len(table_values.columns), 'iti', params.iti*np.ones(ntrials, dtype='int')) 

# Create an array of ntrials random seed values
# I will use them when i create tone clouds
# add these seed values to your table
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
    stim_name = 'training_detection_experiment_index_' + str(index) + '_unitdur_' + str(unitdur) + '_percentage_' + str(percentage) + '.wav'
    table_values.loc[index, 'stim_name'] = stim_name
    
    # Save the audio data to a file in the "stimuli" folder
    file_path = os.path.join(stimuli_dir, stim_name)
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
    table_values.loc[index, 'isi'] = isi_value


# save the data frame
tsv_filename = 'detection_training_block_' + str(block_id) + '_table.tsv'    
table_path = os.path.join(table_dir, tsv_filename)
table_values.to_csv(table_path, sep='\t', index=False)

# Save the signal variable as a pickle file
signal_filename = 'detection_training_block_' + str(block_id) + '_signal.pkl'
signal_path = os.path.join(data_dir, signal_filename)

with open(signal_path, 'wb') as f:
    pickle.dump(signal, f)


# # Load the signal variable from the pickle file
# with open(signal_path, 'rb') as f:
#     loaded_signal = pickle.load(f)