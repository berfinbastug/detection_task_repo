#=====================
# ESTABLISH THE WORKING ENVIRONMENT
#=====================
import sys
default_path = '/home/bastugb/Documents/detection_experiment'
sys.path.append(default_path)

import pandas as pd
import numpy as np
import os

from psychtoolbox import WaitSecs, GetSecs
from psychopy import core, gui, visual
from psychopy.hardware import keyboard
from psychtoolbox import audio, PsychPortAudio
from scipy.io import wavfile
import run_experiment_functions as ef
import data_frame_functions as dff

# experiment specific stuff
import experiment_params as params

#=====================
#DEFINE DIRECTORIES
#=====================
# when I switch to a new computer, just change the main_dir
main_dir = '/home/bastugb/Documents/detection_experiment/training'
stimuli_dir = main_dir + '/stimuli_training'
data_dir = main_dir + '/data_training'
table_dir = main_dir + '/tables_training'

#=====================
#COLLECT PARTICIPANT INFO
#=====================
#-create a dialogue box for participant information
# counterbalance 1: LEFT: YES, RIGHT: NO
# counterbalance 2: LEFT: NO, RIGHT: YES
exp_info = {'counterbalance': 0}
my_dlg = gui.DlgFromDict(dictionary=exp_info)


#=====================
#SET UP THE SYSTEM 
#=====================
# prepare keyboard
kb = keyboard.Keyboard()  # to handle input from keyboard (supersedes event.getKeys())
# create response time clock
timer = core.Clock()

# define the window (size, color, units, fullscreen mode) 
# the size of the window is specific to the screen we are using, also I don't know why I call monitor, a 'testMonitor'
# screen = 1, shows the display window in the booth
# screen = 0, shows the display window in the control room
win = visual.Window([1920, 1080], fullscr=True, monitor="testMonitor", units="cm", screen = 1)


#=====================
#READ THE BLOCK SPECIFIC DATA FRAME 
#=====================
table_name = 'detection_training_block_0_table.tsv'
df, nTrials = dff.get_df(table_name, table_dir)






experiment_start_text = ("Welcome to our experiment. This is a training session.\n"
                         "Please carefully read the following instructions.\n"
                         "\n"
                         "\n"
                         "You can now put on your headphones and proceed with the detailed instructions regarding the experimental procedure.")

ef.display_text(experiment_start_text, win)
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)


experimental_instructions = ("During each block, you will hear long sequences of noise-like sounds. Some of these sequences contain embedded repeating patterns, while others consist of a continuous sequence of sounds with no repeating patterns at all."  
                             "Your task is to listen carefully and report whether or not you hear repeating patterns by answering YES or NO. If you detect repeating patterns, answer YES. If you do not detect repeating patterns, answer NO." 
                             "Try to respond as quickly as possible while maintaining high accuracy.\n"
                             "\n"
                             "\n"
                             "Press any button to continue.")

ef.display_text(experimental_instructions, win)
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)
 


while True:
    df_shuffled = df.sample(frac=1).reset_index(drop=True)  # Shuffle rows
    if dff.check_consecutive_occurrences(df_shuffled['percentage']):
        break




#=====================
#PRELOAD STIMULUI
#=====================
# list the sound filenames, in a randomized way
sound_filenames = df_shuffled['stim_name'].to_list()
# set up the sound file names
stimuli, channels, fs = ef.setup_audio_files(sound_filenames, stimuli_dir, params)

#=====================
#DEFINE STIMULI (STREAM)
#=====================
# which is stream in my case
device_ids = [i_device for i_device, device in enumerate(audio.get_devices()) if params.device_name in device['DeviceName']]
for i_device, device in enumerate(audio.get_devices()):
    if params.device_name in device['DeviceName']:
        print(device['DeviceName'])

assert (len(device_ids) == 1)
params.device_id = device_ids[0]

# Initialize an audio stream with the global sampling rate and channels
stream = [audio.Stream(freq=fs, device_id = params.device_id, channels=channels)]

# play empty sound at first
# Create an empty stimulus buffer with 0.1 seconds duration
stimulus = np.zeros((int(fs*.1), channels))

# Fill the buffer for each slave in the audio stream and start playback
for slave in stream:
    PsychPortAudio('FillBuffer', slave.handle, stimulus)
    PsychPortAudio('Start', slave.handle)

# stream is ready now
stream[0].stimuli = stimuli
    
#=====================
#TIMING PARAMETERS
#=====================
# I need to do something to organize the onset time of each stimulus
# I am planning to do the following thing. for the first stimulus, I will learn the current time and just add 0.5.
# When I start the stream, I get a time stamp of when the stream is actually presented. To learn when I should 
# present the nth sound, I should add (n-1)th soa to the (n-1)th onset time. To accsess to the (n-1)th onset time,
# I will create first list of zeros, the size of this will be ntrial.
tonsets = np.zeros(nTrials)
toffsets = np.zeros(nTrials)  # this is just for fun
# I also need the list of stimulus onset asynchrony (soa or isi)
# In this context, it only matters when participants exceeds the response window.
# It is the maximum amount of waiting time, if they respond earlier, ISI will be defined based on their reaction time
tISI = df_shuffled['isi'].to_list()  # it should be max_isi. there is no consistency in my nomenclature...

#=====================
#PREPARE DATA FRAME TO STORE OUTPUT
#=====================
output_data = pd.DataFrame(columns=params.output_data_columns)

#=====================
#PRESENT INSTRUCTIONS
#=====================
# give the instructions and block related information here
# Welcome to the first session of my experiment. Please carefully read the following instructions. This session consists of 7 blocks. Each block lasts about 11 minutes. There will be short breaks between each block. Use this time to rest and prepare for the next block. 🙂
experiment_start_text = 'press any button to start the training block'
ef.display_text(experiment_start_text, win)
# Wait for any key press to continue
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)

#=====================
#LEARN WHEN THE BLOCK STARTS AND CLEAR THE EXISTING EVENTS IF ANY
#=====================
wakeup = GetSecs() # learn when a block starts.
kb.clearEvents()  # clear any previous keypresses


#=====================
# LOOP OVER TRIALS
#=====================
for itrial in range(nTrials):
    #=====================
    #START TRIAL
    #===================== 
    instruction_text = ef.get_counterbalance_instruction(exp_info['counterbalance'], nTrials, itrial)
    t_trial = ef.display_text(instruction_text, win)
    print(df_shuffled['stim_name'])
    
    # setup trial specific parameters
    row = df_shuffled.loc[itrial]
    max_wait_time = tISI[itrial]
    stim = stream[0].stimuli[row['stim_name']]
    stream[0].fill_buffer(stim)

    # arrange timing
    # for the first trial, presentation time is half a second after the start of the trial
    if itrial == 0:
        onset_time = wakeup + 0.5
    # after the first trial, the onset_time will be saved to the tonsets
    else:
        onset_time = tonsets[itrial-1]+ reaction_time + row['iti']

    # present stimuli and collect responses
    tonset = stream[0].start(when = onset_time, wait_for_start = 1)
    tonsets[itrial] = tonset  # update onset times
    
    # reset the clock
    kb.clock.reset()

    # get the keys
    keys = kb.waitKeys(maxWait= max_wait_time, keyList= ['2', '3', 'escape'], waitRelease=True)
    
    if keys is not None:
        stream[0].stop()
        if keys[0].name == 'escape':
            core.quit()
        else:
            reaction_time, name, tDown, button_press_duration = ef.get_key_values_when_response(keys)
            actual_response = ef.check_response(exp_info['counterbalance'], name)

    else:
        reaction_time, name, tDown, button_press_duration = ef.get_key_values_when_noresponse(max_wait_time)
    

    output_data = pd.concat([output_data, pd.DataFrame({'participant_id': 0,
                                                        'time': 0,
                                                        'block_idx': 0,
                                                        'trial_idx': [itrial + 1],
                                                        'rt': reaction_time,
                                                        'key_name': name,
                                                        'key_tDown': tDown,
                                                        'button_press_duration': button_press_duration,
                                                        'stim_code': row['stim_code'],
                                                        'unitdur': row['unitdur'],
                                                        'percentage': row['percentage'],
                                                        'expected_response': row['expected_response'],
                                                        'actual_response': actual_response,
                                                        'counterbalance_condition': exp_info['counterbalance']})])
    
# dff.save_output_df(output_data, 'shuffled_training_table.tsv', 0, data_dir)
percent_correct = ef.calculate_performance(output_data)
feedback_text = f'Percentage correct is: {percent_correct}%, press any button to continue'
ef.display_text(feedback_text, win)
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)

stream[0].close()

experiment_end_text = 'end of the training, press any button to end the session'
ef.display_text(experiment_end_text, win)
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)

# end session by closing the window completely
win.close()