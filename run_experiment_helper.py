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
def setup_audio(sound_filenames, stim_for_block, params):

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

    # Open audio stream
    print(audio.get_devices())
    device_ids = [i_device for i_device, device in enumerate(audio.get_devices()) if device['DeviceName'] == params.device_name]
    print(device_ids)
    assert (len(device_ids) == 1)
    params.device_id = device_ids[0]

    # Initialize an audio stream with the global sampling rate and channels
    stream = [audio.Stream(freq=fs, channels=channels, device_id = params.device_id)]
	
    # I DON'T HAVE FEEDBACK FILES, AT LEAST FOR NOW
    # if len(feedback_filenames) == 0:
    #     stream = [audio.Stream(
    #     freq=fs, channels=channels, device_id= setup_audio_parameters['device_id'])]
    # else:
    #     master = audio.Stream(
    #     freq=fs, channels=channels, device_id=setup_audio_parameters['device_id'], mode=9)
    #     stream = [audio.Slave(master.handle) for i in range(3)]
    #     PsychPortAudio('Start', master.handle)

    # play empty sound at first
    # Create an empty stimulus buffer with 0.1 seconds duration
    stimulus = np.zeros((int(fs*.1), channels))
    
    # Fill the buffer for each slave in the audio stream and start playback
    for slave in stream:
        PsychPortAudio('FillBuffer', slave.handle, stimulus)
        PsychPortAudio('Start', slave.handle)

    # stream is ready now
    stream[0].stimuli = stimuli

    return stream



#=====================
#DISPLAY INSTRUCTION
#====================
def display_instruction(string, win):
    if win is not None:
        text = visual.TextStim(
            win, text=string
        )
        text.draw()
        win.flip()
    print(string)
    t_instruction = GetSecs()
    return t_instruction



#=====================
#DISPLAY FEEDBACK
#====================
def display_feedback(correction_detail, win, stream, args, response_time_end=None, wait_to_end=False):
    feedback = args.feedback[correction_detail]
    if feedback is None:
        WaitSecs(response_time_end-GetSecs())
        t_feedback = None
    else:
        if '.wav' in feedback:
            stimulus = stream[0].stimuli[feedback]
            stream[1].fill_buffer(stimulus)
            stream[1].start()
            t_feedback = None
        else:
            t_feedback = display_instruction(
                feedback, win
            )
        if wait_to_end:
            WaitSecs(response_time_end-GetSecs())
            display_trial(win, args)
            t_feedback = None
    return t_feedback



#=====================
#PARSE RESPONSE
#====================
def parse_response(keys, expected_response, t_stimulus,
                   response_keys, response_time_window, feedback_direct=False):


    if keys is not None:
        response = response_keys[keys[0].name]
        if response == 'quit':
            core.quit()
        if feedback_direct:
            correction_detail = response
        else:
            if response == expected_response:
                correction_detail = 'correct'
            elif response != expected_response:
                if expected_response in response_keys.values():
                    correction_detail = 'incorrect'
                else:
                    correction_detail = 'false_alarm'
        t_button = keys[0].tDown
        reaction_time = t_button-t_stimulus
        if reaction_time < response_time_window[0]:
            correction_detail = 'false_alarm'
    else:
        response = 'none'
        reaction_time = float('inf')
        t_button = float('inf')
        if expected_response in response_keys.values():
            correction_detail = 'miss'
        else:
            correction_detail = 'correct_rejection'
    return correction_detail, reaction_time, response, t_button



#=====================
#GET STIMULUS TIME
#====================
def get_stimulus_time(index, df, args):
    if args.is_absolute_time:
        # Start audio at specified absolute time
        t_stimulus = df.loc[index, 'stimulus_time']
    else:
        # or start audio after an inter trial interval
        now = GetSecs()
        if args.is_compute_isi:
            jitter = args.inter_trial_interval_jitter_range
            inter_trial_interval = (np.random.rand()*np.diff(jitter) + jitter[0])[0]
            df.loc[index, 'inter_trial_interval'] = inter_trial_interval
        t_stimulus = now + df.loc[index, 'inter_trial_interval']
    df.loc[index, 't_stimulus'] = t_stimulus
    return t_stimulus


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
    table_name = f'block_{which_block}_randomized_table.tsv'
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

