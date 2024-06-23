#=====================
#STIMULUS RELATED PARAMETERS
#=====================
# DURATION, IV 1
# independent variable
# Leo participated in the pilot experiment in 27.03.2024. 
# In his version, I was using one duration condition. He told me that
# he used the rhythm induced by the duration as a template to detect repetition. 
# To prevent this, I am adding other duration conditions to my detection experiment right now (28.03.2024)
min_unit_dur = 0.4  
max_unit_dur = 1
n_unit_dur_cond = 3

# PROPORTION OF THE REPEATING TONES, IV 2
min_rep_percentage = 0  # Define the start point
max_rep_percentage = 1  # define the end point
n_rep_percentage_cond = 10  # define the number of elements

nblocks = 3
iti = 1  # inter trial interval

#=====================
#OUTPUT
#=====================
# planning to change this!
keys_output_columns = ['participant_id', 'time', 'block_idx',
                       'trial_idx', 'rt', 'key_name', 'key_tDown', 
                       'button_press_duration', 'stim_code', 'unitdur', 
                       'percentage', 'expected_response', 'actual_response', 'counterbalance_condition']

#=====================
#SET UP AUDIO PARAMETERS
#=====================
# device_name = 'US-4x4HR: USB Audio (hw:0,0)'
# device_name = 'MacBook Pro Speakers'
device_name = 'EarPods'
device_id = 1
stimulus_rms = 1
