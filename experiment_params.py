#=====================
#DIRECTORY NAMES
#=====================
main_dir = '/Users/bastugb/Desktop/detection_experiment'
data_dir  =  '/Users/bastugb/Desktop/detection_experiment/data'  
sound_dir = '/Users/bastugb/Desktop/detection_experiment/stimuli'
table_dir = '/Users/bastugb/Desktop/detection_experiment/tables'  
#=====================
#STIMULUS RELATED PARAMETERS
#=====================
# DURATION, IV 1
# independent variable 1
min_unit_dur = 0.4  
max_unit_dur = 0.4  
n_unit_dur_cond = 1 
# REPEATING PERCENTAGE OF THE TONES, IV 2
min_rep_percentage = 0  # Define the start point
max_rep_percentage = 1  # define the end point
n_rep_percentage_cond = 10  # define the number of elements

nblocks = 4
#=====================
#NO NAME YET
#=====================
response_keys = ['y', 'n']
keys_output_columns = ['block_idx','trial_idx', 'rt','key_name', 'key_tDown', 'button_press_duration','stim_code']
iti = 1  # inter trial interval
#=====================
#SET UP AUDIO PARAMETERS
#=====================
# device_name = 'US-4x4HR: USB Audio (hw:0,0)'
# device_name = 'MacBook Pro Speakers'
device_name = 'EarPods'
device_id = 1
stimulus_rms = 1
