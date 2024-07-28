"""
code to run the detection experiment
28.07.2024
berfin bastug
"""
# to dos
# change the name of the experimental blocks you read
#=====================
# ESTABLISH THE WORKING ENVIRONMENT
#=====================
import pandas as pd
import numpy as np
import os

from psychopy import core, gui, visual
from psychopy.hardware import keyboard

from psychtoolbox import audio, PsychPortAudio
from psychtoolbox import GetSecs

import data_frame_functions as dff

import experiment_params as params # experiment specific stuff
import run_experiment_functions as ef

#=====================
#DEFINE DIRECTORIES
#=====================
# when I switch to a new computer, just change the main_dir
main_dir = '/Users/bastugb/Desktop/detection_experiment'
stimuli_dir = main_dir + '/stimuli'
data_dir = main_dir + '/data'
table_dir = main_dir + '/tables'

#=====================
#COLLECT PARTICIPANT INFO
#=====================
#-create a dialogue box for participant information
# counterbalance 1: LEFT: YES, RIGHT: NO
# counterbalance 2: LEFT: NO, RIGHT: YES
exp_info = {'participant_id':0, 'age':0, 'handedness':('right','left','ambi'), 'counterbalance': 0}
my_dlg = gui.DlgFromDict(dictionary=exp_info)

# check for valid part0icipant data, make sure subject data is entered correctly
if exp_info['participant_id'] ==0: # nothing entered
#     #create another dialog box (not from a dictionary because we're just showing an error message)
    err_dlg = gui.Dlg(title='error message') #give the dlg a title
    err_dlg.addText('Enter a valid subject number!') #create an error message
    err_dlg.show() #show the dlg
    core.quit() #quit the experiment
    
# get date and time
time_stamp = ef.get_datetime_string()[0]
exp_info['time'] = time_stamp

# create a unique filename for the data
# don't forget to turn integers into strings for the filename, don't forget to add the filetype at the end: csv, txt...
experiment_mark = 'detection_experiment_toneclouds_pid' + str(exp_info['participant_id']) + '_' + exp_info['time'] + '.tsv'

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


experiment_start_text = ("Welcome to our experiment.\n"
                         "Please carefully read the following instructions.\n"
                         "\n"
                         "\n"
                         "You can press any button to continue to the next page.")

ef.display_text(experiment_start_text, win)
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)

experiment_details_text = ("This session consists of 7 blocks. Each block lasts about 11 minutes." 
                           "There will be short breaks between each block. Use this time to rest and prepare for the next block.\n"
                           "\n"
                           "\n" 
                           "Continue for detailed instructions about the experimental procedure.")

ef.display_text(experiment_details_text, win)
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)

experimental_instructions = ("During each block, you will hear long sequences of noise-like sounds. Some of these sequences contain repeating chunks, while others do not."  
                             "Your task is to listen carefully and report whether or not you hear repeating chunks by answering 'yes' or 'no.' If you detect repeating chunks, answer 'yes.' If you do not detect repeating chunks, answer no." 
                             "Try to respond as quickly as possible while maintaining high accuracy.\n"
                             "\n"
                             "\n"
                             "Press any button to continue.")

ef.display_text(experimental_instructions, win)
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)


# learn nblocks and call non-randomized blocks
files_in_tabledir = os.listdir(table_dir)
blocks = [file for file in files_in_tabledir if file.endswith('.tsv')]
nBlocks = params.nblocks

#=====================
# LOOP OVER BLOCKS
#=====================
for iblock in range(1):  
    which_block = iblock + 1

    #=====================
    #READ THE BLOCK SPECIFIC DATA FRAME 
    #=====================
    table_name = f'detection_experiment_block_{which_block}_table.tsv'
    df, nTrials = dff.get_df(table_name, table_dir)

    #=====================
    #SHUFFLE THE DATA FRAME
    #=====================
    # pseudo randomize the data frame for each individual
    # condition: any value should not occur more than three times consecutively
    # shuffle dataframe rows until the condition is met
    # save this shuffled table immediately before you forget
    df_shuffled = dff.pseudorandomize_and_save_df(df, which_block, exp_info, table_dir)

    #=====================
    #PRELOAD STIMULUI
    #=====================
    # list the sound filenames, in a randomized way
    sound_filenames = df_shuffled['stim_name'].to_list()
    # search the sound in a specific block folder
    stim_for_block = os.path.join(stimuli_dir,f'detection_experiment_block{which_block}')  
    # set up the sound file names
    stimuli, channels, fs = ef.setup_audio_files(sound_filenames, stim_for_block, params)
    
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
    tISI = df_shuffled['max_isi'].to_list()

    #=====================
    #PREPARE DATA FRAME TO STORE OUTPUT
    #=====================
    output_data = pd.DataFrame(columns=params.output_data_columns)

    #=====================
    #PRESENT INSTRUCTIONS
    #=====================
    # give the instructions and block related information here
    # Welcome to the first session of my experiment. Please carefully read the following instructions. This session consists of 7 blocks. Each block lasts about 11 minutes. There will be short breaks between each block. Use this time to rest and prepare for the next block. 🙂
    experiment_start_text = 'Welcome to our experiment.\n' + 'Please carefully read the following instructions. '
    block_start_text = f'Block {which_block} of {nBlocks}\n' + 'Press any button to start'
    ef.display_text(block_start_text, win)
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
    for itrial in range(2):
        #=====================
        #START TRIAL
        #===================== 
        instruction_text = ef.get_counterbalance_instruction(exp_info['counterbalance'], nTrials, itrial)
        t_trial = ef.display_text(instruction_text, win)
        
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
        

        output_data = pd.concat([output_data, pd.DataFrame({'participant_id': exp_info['participant_id'],
                                                            'time': exp_info['time'],
                                                            'block_idx': which_block,
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
        
    dff.save_output_df(output_data, experiment_mark, which_block, data_dir)
    percent_correct = ef.calculate_performance(output_data)
    feedback_text = f'Percentage correct is: {percent_correct}%, press any button to continue'
    ef.display_text(feedback_text, win)
    kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)

    stream[0].close()

experiment_end_text = 'end of the experiment, press any button to end the experiment'
ef.display_text(experiment_end_text, win)
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)

# end session by closing the window completely
win.close()

 
    


