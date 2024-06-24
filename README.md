stim_production.py
Define directories
Define variables (duration and proportion of the repeating tones)
Create a data frame: it starts with generating a baseline list. In the baseline list, there are block, unitdur, percentage, stim_code, expected_response.
Add other variables: iti, seed (you use this seed as a parameter while generating tone clouds. This ensures that all tone clouds in an experimental session are random).
At that point, by using the values in the table, generate signals. 
To generate signals, you use a function called gencloudcoherence. It takes change_dictionary as an input. The output of the functions are the signal itself (y) and the parameters of the tone clouds (sP). You can find more detailed information in the part where I explain the function itself. 
Give each signal a name. Store the name of the audio signals in the table.
Write the signal as wav files.
Extract values from sP dictionary and add them as new columns to table values.
Calculate signal length and the stimulus duration values. Attach these values to the data frame as new columns. 
Lastly, calculate the maximum inter stimulus interval and attach it to the data frame.
In the end we have the following columns: block, unitdur, percentage, stim_code, expected_response, iti, seed, stim_name, lowf, highf, fstep, timestep, tonedur, nrep, rtime, fs, signal_length, stim_duration, max_isi

experiment_params.py
Stimulus related parameters:
Duration
Proportion of repeating tones
Number of blocks
Inter trial interval (iti)
Output column names → participant_id, time, block_idx, trial_idx, rt, key_name, key_tDwon, button_press_duration, stim_code, unitdur, percentage, expected_response, actual_response, counterbalance_condition
Audio parameters

stimulus_params.py
Low frequency 
High frequency
Frequency step
Time step
Tone duration
Unit duration
Number of repetition
Percentage
Seed
Rise time
Sampling frequency

tone_cloud_production.py
This function generates tone clouds stimulus with specified frequency and time perturbations and repeated tones. It ensures reproducibility with a random seed and allows customization through parameter changes. The generated signal is normalized and padded to avoid clipping and ensure proper alignment.

ramp_function.py
The psyramp function is designed to apply a cosine-squared ramp (fade-in and fade-out) to a signal x. This can be useful in audio processing to smoothly transition the start and end of a signal to avoid abrupt changes, which can create clicks or other unwanted artifacts. 

pseudorandomization.py
This script provides functions for pseudorandomizing a DataFrame and ensuring specific conditions are met before saving the shuffled DataFrame as a TSV file. There are two functions: 
(1) check_consecutive_occurrences: Verifies that no value in an array occurs more than three times consecutively.
(2) shuffled_df: Shuffles the rows of a DataFrame until no percentage value appears more than three times consecutively, then saves the shuffled DataFrame as a TSV file.
