from psychopy.hardware import brainproducts
from psychtoolbox import WaitSecs, GetSecs
from psychtoolbox import audio, PsychPortAudio
from psychopy import visual, core
import os.path as op
import pandas as pd
import numpy as np
import soundfile as sf
from datetime import datetime
import pkg_resources
import experiment_params



#=====================
#GET DATE TIME AS STRING
#=====================
def get_datetime_string():
    now = datetime.now()
    return now.strftime("%Y%m%d_%H%M%S"), now.strftime("%Y%m%d")



#=====================
#SET UP AUDIO
#====================
def setup_audio_files(sound_filenames, stim_for_block, params):

    # Preload stimuli from wav-file
    stimuli = {}
    # filenames = stimulus_filenames+feedback_filenames
    fs = channels = None
    stim_rms = params.stimulus_rms

    for filename in sound_filenames:
        
        # Construct the full filepath for the current sound file
        filepath = op.join(stim_for_block, filename)

        if len(filename) == 0:
            continue

        # Read the sound file using the soundfile library (sf)
        y, fs_file = sf.read(filepath)
        
        # Determine the number of channels in the sound file
        channels_file = 1 * (y.ndim < 2) or y.shape[1]
				
        # Update the global sampling rate (fs) and channels based on the current sound file
        if fs is None:
            fs = fs_file
            channels = channels_file
				
        # Check that the global sampling rate and channels match the current sound file
        assert (fs == fs_file)
        assert (channels == channels_file)
				
        # Add the sound data multiplied by the stimulus RMS to the stimuli dictionary
        stimuli[filename] = y*stim_rms

        # I DON'T HAVE FEEDBACK FILES, AT LEAST FOR NOW
        # if len(feedback_filenames) == 0:
        #     stream = [audio.Stream(
        #     freq=fs, channels=channels, device_id= setup_audio_parameters['device_id'])]
        # else:
        #     master = audio.Stream(
        #     freq=fs, channels=channels, device_id=setup_audio_parameters['device_id'], mode=9)
        #     stream = [audio.Slave(master.handle) for i in range(3)]
        #     PsychPortAudio('Start', master.handle)
    return stimuli, channels, fs



#=====================
#DISPLAY INSTRUCTION
#====================
def display_text(string, win):
    if win is not None:
        text = visual.TextStim(
            win, text=string
        )
        text.draw()
        win.flip()
    print(string)
    t_text = GetSecs()
    return t_text



#=====================
#CHECK RESPONSE
#====================
def check_response(counterbalance_info, key_name):
    if (counterbalance_info == 1) & (key_name == '2'):
        # LEFT: YES, RIGHT: NO
        # 1 stands for saying yes
        # 0 stands for saying no
        actual_response = 1
    elif (counterbalance_info == 2) & (key_name == '2'):
        # LEFT: NO, RIGHT: YES
        actual_response = 0
    elif (counterbalance_info == 1) & (key_name == '3'):
        actual_response = 0
    elif (counterbalance_info == 2) & (key_name == '3'):
        actual_response = 1
    
    return actual_response



#=====================
#CALCULATE PERFORMANCE
#====================
def calculate_performance(keys_output)
    total_cases = len(keys_output)
    matching_cases = (keys_output['expected_response'] == keys_output['actual_response']).sum()
    percentage_matching = (matching_cases/total_cases)*100
    return percentage_matching



#=====================
#SHORTER VERSION OF PARSE RESPONSE
#====================
def get_key_values_when_response(keys):

    reaction_time = keys[0].rt
    name = keys[0].name
    tDown = keys[0].tDown
    button_press_duration = keys[0].duration
    return reaction_time, name, tDown, button_press_duration


def get_key_values_when_noresponse(max_wait_time):

    reaction_time = max_wait_time
    name = 'no_response'
    tDown = 0
    button_press_duration = 0
    return reaction_time, name, tDown, button_press_duration


def get_df(which_block, params):

    # read out the data frame, it is pseudorandomized
    table_name = f'block_{which_block}_table.tsv'
    table_for_block = op.join(params.table_dir, table_name)
    df = pd.read_csv(table_for_block, sep = '\t')
    nTrials = len(df)
    return df, nTrials


#=====================
#SAVE OUPUT
#====================
def save_output(output, experiment_mark, which_block, params):
    file_name = 'block_no_'+str(which_block)+ '_' + experiment_mark
    output_data_directory = op.join(params.data_dir, file_name)
    output.to_csv(output_data_directory, sep='\t', index=False)

