#=====================
# ESTABLISH THE WORKING ENVIRONMENT
#=====================
import pandas as pd
import numpy as nps
import os

from psychtoolbox import WaitSecs, GetSecs
from psychopy import core, gui, visual, event, monitors
from psychopy.hardware import keyboard
import psychopy.parallel as parallel


from run_experiment_helper import display_instruction,\
    setup_audio_files, display_feedback, parse_response,\
    get_datetime_string, get_key_values_when_response, get_key_values_when_noresponse, get_df,\
    save_output

from pseudorandomization import shuffled_df
# experiment specific stuff
import experiment_params as params


#=====================
#COLLECT PARTICIPANT INFO
#=====================
#-create a dialogue box for participant information
# counterbalance 1: LEFT: YES, RIGHT: NO
# counterbalance 2: LEFT: NO, RIGHT: YES
exp_info = {'participant_id':0, 'age':0, 'handedness':('right','left','ambi'), 'counterbalance': 0}
# my_dlg = gui.DlgFromDict(dictionary=exp_info)

# # check for valid participant data, make sure subject data is entered correctly
# if exp_info['participant_id'] ==0: # nothing entered
#     #create another dialog box (not from a dictionary because we're just showing an error message)
#     err_dlg = gui.Dlg(title='error message') #give the dlg a title
#     err_dlg.addText('Enter a valid subject number!') #create an error message
#     err_dlg.show() #show the dlg
#     core.quit() #quit the experiment
    
# get date and time
time_stamp = get_datetime_string()[0]
exp_info['time'] = time_stamp

# create a unique filename for the data
# don't forget to turn integers into strings for the filename, don't forget to add the filetype at the end: csv, txt...
experiment_mark = 'detection_task_toneclouds_pid' + str(exp_info['participant_id']) + '_' + exp_info['time'] + '.tsv'

#=====================
#SET UP THE SYSTEM 
#=====================
# prepare keyboard
kb = keyboard.Keyboard()  # to handle input from keyboard (supersedes event.getKeys())
# create response time clock
timer = core.Clock()
# define the window (size, color, units, fullscreen mode) 
win = visual.Window([800,600], fullscr=False, monitor="testMonitor", units="cm")

#=====================
# LOOP OVER BLOCKS
#=====================
# learn nblocks
# counterbalance the order of block presentation
# i think in my case there is no need for counterbalancing because all blocks are similar
files_in_tabledir = os.listdir(params.table_dir)
blocks = [file for file in files_in_tabledir if file.endswith('.tsv')]
nBlocks = params.nblocks

for iblock in range(1):
    #=====================
    #PRESENT INSTRUCTIONS
    #=====================
    which_block = iblock + 1
    # read out the data frame
    df, nTrials = get_df(which_block, params)
    # pseudorandomize the data frame
    random_df = shuffled_df(df, params.table_dir, exp_info['participant_id'], which_block)

    #=====================
    #PRELOAD STIMULUI
    #=====================
    # COMPLETED
    # list the sound filenames, in a randomized way
    sound_filenames = df['stim_name'].to_list()
    # this directory is necessary while reading from wav-files
    # search the sound in a specific block folder
    stim_for_block = os.path.join(params.sound_dir,f'block{which_block}')  
    # define stimuli, which is stream in my case
    # setup audio stream 
    # Open audio stream

    print(audio.get_devices())
    device_ids = [i_device for i_device, device in enumerate(audio.get_devices()) if device['DeviceName'] == params.device_name]
    print(device_ids)
    assert (len(device_ids) == 1)
    params.device_id = device_ids[0]

    # Initialize an audio stream with the global sampling rate and channels
    stream = [audio.Stream(freq=fs, channels=channels, device_id = params.device_id)]
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

    stream = setup_audio(sound_filenames, stim_for_block, params)
    # give the instructions and block related information here
    block_start_text = f'Block {which_block} of {nBlocks}\n' + 'Press any button to start'
    display_instruction(block_start_text, win)
    # Wait for any key press to continue
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
    # I also need the list of stimulus onset asynchrony (soa or isi)
    # In this context, it only matters when participants exceeds the response window.
    # It is the maximum amount of waiting time, if they respond earlier, ISI will be defined based on their reaction time
    tISI = df['ISI'].to_list()

    #=====================
    #PREPARE DATA FRAME TO STORE OUTPUT
    #=====================
    keys_output = pd.DataFrame(columns=params.keys_output_columns)
    
    #=====================
    #LEARN WHEN THE BLOCK STARTS AND CLEAR THE EXISTING EVENTS IF ANY
    #=====================
    wakeup = GetSecs() # learn when a block starts.When I have multiple blocks, I should also store this as a list. For now, it is okay
    kb.clearEvents()  # clear any previous keypresses

    #=====================
    # LOOP OVER TRIALS
    #=====================
    for itrial in range(10):
        #=====================
        #START TRIAL
        #===================== 
        block_start_text = f'Block {which_block} of {nBlocks}\n' + 'Press space bar to start'
        t_trial = display_instruction(f'Trial {itrial + 1} of {10}\n', win)
        
        # setup trial specific parameters
        row = df.loc[itrial]
        stim_dur = row['stim_duration'] 
        stim_code = row['stim_code']
        max_wait_time = tISI[itrial]
        stim = stream[0].stimuli[row['stim_name']]
        stream[0].fill_buffer(stim)

        # arrange timing
        # for the first trial, presentation time is half a second after the start of the trial
        if itrial == 0:
            onset_time = wakeup + 0.5
        # after the first trial, the onset_time will be saved to the tonsets
        else:
            onset_time = tonsets[itrial-1]+ reaction_time + params.wait_after_rt

        # present stimuli and collect responses
        tonset = stream[0].start(when = onset_time, wait_for_start = 1)
        tonsets[itrial] = tonset  # update onset times
        
        # reset the clock
        kb.clock.reset()

        # get the keys
        keys = kb.waitKeys(maxWait= max_wait_time, keyList= params.response_keys, waitRelease=True)
        
        if keys is not None:
            stream[0].stop()
            reaction_time, name, tDown, button_press_duration = get_key_values_when_response(keys)

        else:
            reaction_time, name, tDown, button_press_duration = get_key_values_when_noresponse(max_wait_time)
        

        keys_output = pd.concat([keys_output, pd.DataFrame({'block_idx': which_block,
                                               'trial_idx': [itrial+1],
                                               'rt': reaction_time,
                                               'key_name': name,  
                                               'key_tDown': tDown,
                                               'button_press_duration': button_press_duration,
                                               'stim_code': stim_code})])
        

        save_output(keys_output, experiment_mark,which_block, params)



    # % END SESSION
    win.close()

 
    

    
    

    # TO DO: define the monitor settings 


    # TO DO: make mouse pointer invisible

