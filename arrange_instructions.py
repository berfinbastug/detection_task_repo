"""
code to run the detection experiment
23.07.2024
berfin bastug
"""
# to dos
# change the name of the experimental blocks you read
#=====================
# ESTABLISH THE WORKING ENVIRONMENT
#=====================
from shutil import which
import pandas as pd
import numpy as np
import os

from psychopy import core, gui, visual
from psychopy.hardware import keyboard
import psychopy.parallel as parallel

from psychtoolbox import audio, PsychPortAudio
from psychtoolbox import GetSecs

import data_frame_functions as dff

import experiment_params as params # experiment specific stuff
import run_experiment_functions as ef

#=====================
#DEFINE DIRECTORIES
#=====================
# when I switch to a new computer, just change the main_dir


#=====================
#COLLECT PARTICIPANT INFO
#=====================
#-create a dialogue box for participant information
# counterbalance 1: LEFT: YES, RIGHT: NO
# counterbalance 2: LEFT: NO, RIGHT: YES
exp_info = {'participant_id':0, 'age':0, 'handedness':('right','left','ambi'), 'counterbalance': 0}

# get date and time
time_stamp = ef.get_datetime_string()[0]
exp_info['time'] = time_stamp


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

experiment_start_text = ("Welcome to our experiment.\n Please carefully read the following instructions.\n"
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


#=====================
# LOOP OVER BLOCKS
#=====================
nBlocks = 2
for iblock in range(nBlocks):  
    which_block = iblock + 1

    #=====================
    #PRESENT INSTRUCTIONS
    #=====================
    # give the instructions and block related information here
    # 


    block_start_text = f'Block {which_block} of {nBlocks}\n' + 'Press any button to start'
    ef.display_text(block_start_text, win)
    # Wait for any key press to continue
    kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)



experiment_end_text = 'end of the experiment, press any button to end the experiment'
ef.display_text(experiment_end_text, win)
kb.waitKeys(keyList=['1', '2', '3', '4'], waitRelease=True)

# end session by closing the window completely
win.close()

 
    


