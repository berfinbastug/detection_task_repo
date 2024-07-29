#=====================
# ESTABLISH THE WORKING ENVIRONMENT
#=====================
import sys
default_path = '/Users/bastugb/Desktop/tapping_experiment'
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
main_dir = '/Users/bastugb/Desktop/tapping_experiment/training'
stimuli_dir = main_dir + '/stimuli_training'
data_dir = main_dir + '/data_training'
table_dir = main_dir + '/tables_training'

#=====================
#COLLECT PARTICIPANT INFO
#=====================
# there is no need to collect participant info during the training block
#-create a dialogue box for participant information

#=====================
#READ THE TRAINING DATA FRAME 
#=====================
table_name = f'tapping_training_block_0_table.tsv'
df, nTrials = dff.get_df(table_name, table_dir)

#=====================
#PRELOAD STIMULUI
#=====================
# list the sound filenames, in a randomized way
sound_filenames = df['stim_name'].to_list()
# this directory is necessary while reading from wav-files

# define stimuli, which is stream in my case
# setup audio stream 
stimuli, channels, fs = ef.setup_audio_files(sound_filenames, stimuli_dir, params)

device_ids = [i_device for i_device, device in enumerate(audio.get_devices()) if params.device_name in device['DeviceName']]
for i_device, device in enumerate(audio.get_devices()):
    if params.device_name in device['DeviceName']:
        print(device['DeviceName'])

assert (len(device_ids) == 1)
params.device_id = device_ids[0]
# print(audio.get_devices())

#=====================
#DEFINE STIMULI (STREAM)
#=====================
# Initialize an audio stream with the global sampling rate and channels
# channels = [channels, 2], here 2 corresponds to the channel of the output (microphone and the looped audio signal)
# the first channels value, which is 1, correspond to the input of the channel, which is the sent audio signal
stream = [audio.Stream(freq=fs, device_id = params.device_id, mode = 3, latency_class = 3, channels=[channels, 2])]

#=============
# THIS PART IS CRUCIAL
# now something like this is necessary I think 
# to record the audio from the microphone people tap
stream[0].get_audio_data(secs_allocate = 1000)
#=============

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
#SET UP THE SYSTEM 
#=====================
# prepare keyboard
kb = keyboard.Keyboard()  # to handle input from keyboard (supersedes event.getKeys())
# create response time clock, to be honest, I am not sure whether I am using this one currently?
timer = core.Clock()

# define the window (size, color, units, fullscreen mode) 
# screen = 1, shows the display window in the booth
# screen = 0, shows the display window in the control room
win = visual.Window([1920, 1080], fullscr=True, monitor="testMonitor", units="cm", screen = 1)


experiment_start_text = ("Welcome to our experiment. This is a training session.\n"
                         "Please carefully read the following instructions.\n"
                         "\n"
                         "\n"
                         "You can press any button to continue to the next page.")

ef.display_text(experiment_start_text, win)
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)


training_instructions = ("During the experiment, you will hear long sequences of noise-like sounds."
                             "Your task is to tap your finger next to the attached microphone as soon as you hear the sound and sustain your tapping until the end of the sound sequence." 
                             "Some of these sound sequences contain repeating chunks. Try to detect these repeating chunks, and when you do, tap in synchrony with them." 
                             "This means aligning each tap with each repeating chunk and tapping at the same speed as the repeating chunks.\n" 
                             "The repeating chunks are present in most trials, sometimes obvious and sometimes not. In any case, try your best to detect the repetitions and tap in sync with them." 
                             "If you do not detect any repeating chunks, just continuously tap your finger with any rhythm or speed you wish.\n"
                             "\n"
                             "Press any button to continue.")

ef.display_text(training_instructions, win)
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)

training_introduce_fastest_sound = ("You will encounter three different speeds in the blocks.\n"
                             "\n"
                             "Press any button to hear a sequence with the fastest speed")

ef.display_text(training_introduce_fastest_sound, win)
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)





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
max_stim_duration = df_shuffled['stim_duration'].max()
min_stim_duration = df_shuffled['stim_duration'].min()

# I also need the list of stimulus onset asynchrony (soa or isi)
# In this context, it only matters when participants exceeds the response window.
# It is the maximum amount of waiting time, if they respond earlier, ISI will be defined based on their reaction time
tISI = df_shuffled['isi'].to_list()

#=====================
#PREPARE DATA FRAME TO STORE OUTPUT
#=====================
output_data = pd.DataFrame(columns=params.output_data_columns)

#=====================
#LEARN WHEN THE BLOCK STARTS AND CLEAR THE EXISTING EVENTS IF ANY
#=====================
wakeup = GetSecs() # learn when a block starts.When I have multiple blocks, I should also store this as a list. For now, it is okay
kb.clearEvents()  # clear any previous keypresses

#=====================
# LOOP OVER TRIALS
#=====================
stream[0].get_audio_data()  # I think I am doing this to clear the buffer just before the recording
for itrial in range(2):
    #=====================
    #START TRIAL
    #===================== 
    print(itrial)
    t_trial = ef.display_instruction(f'Trial {itrial + 1} of {nTrials}\n', win)
    
    # setup trial specific parameters
    row = df_shuffled.loc[itrial]
    stim_dur = row['stim_duration']
    stim_code = row['stim_code']
    stim = stream[0].stimuli[row['stim_name']]
    stream[0].fill_buffer(stim)

    # arrange timing
    # for the first trial, presentation time is half a second after the start of the trial
    if itrial == 0:
        onset_time = wakeup + 0.5
    # after the first trial, the onset_time will be saved to the tonsets
    else:
    # following trials, the stimulus onset is calculated based on the previous
    # trial's onset time and a specified inter-stimulus interval
        onset_time = tonsets[itrial-1]+ tISI[itrial-1]

    # present stimuli and collect responses
    tonset = stream[0].start(when = onset_time, wait_for_start = 1)
    WaitSecs(stim_dur)
    # just after that while playing the audio, simultaneously record the microphone outpu
    # current_audio_data, absrecposition, overflow, cstarttime = stream[0].get_audio_data(min_secs = min_stim_duration + 1)
    current_audio_data, absrecposition, overflow, cstarttime = stream[0].get_audio_data(min_secs = stim_dur + 1)
    
    tonsets[itrial] = tonset  # update onset times
    toffsets[itrial] = GetSecs()

    sound_name = 'block_' + str(which_block) + '_itrial_' + str(itrial) + '_stimcode_' + str(stim_code) + '_unitdur_' + str(row['unitdur']) + '_percentage_' + str(row['percentage']) +  '_' + experiment_mark
    output_stim_directory = subject_block_specific_path + '/' + sound_name
    wavfile.write(output_stim_directory, fs, current_audio_data)
    tmp_df = pd.DataFrame({'participant_id': exp_info['participant_id'],
                            'time': exp_info['time'],
                            'block_idx': [which_block],
                            'trial_idx': [itrial], 
                            'tapping_file_name': [sound_name],
                            'stim_code': [row['stim_code']],
                            'unitdur': [row['unitdur']],
                            'percentage': [row['percentage']]})
    output_data = pd.concat([output_data, tmp_df], ignore_index=True)

# save the name of the wav files at the end of an each block    
dff.save_tapping_output(subject_block_specific_path, output_data, exp_info['participant_id'], which_block)
stream[0].close()

experiment_end_text = 'end of the experiment, press any bar to end the experiment'
ef.display_text(experiment_end_text, win)
# Wait for any key press to continue
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)

win.close()
