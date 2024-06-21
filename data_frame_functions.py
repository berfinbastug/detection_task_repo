import itertools
import os.path as op
import pandas as pd

#=====================
#GENERATE BASELINE TABLE
#====================
# this function generates a list of trial conditions for an experiment 
# based on the provided parameters. 
# It creates combinations of unit durations and repetition percentages and assigns a specific stimulus code 
# for each combination, along with expected responses. 

# column 1: unit duration
# column 2: repetition percentage
# column 3: stimulus code
# column 4: expected response   
def generate_baseline_table(unit_dur_list, rep_percentage_list, n_percentage_zero, n_rest):
    
    # first, generate bunch of lists
    table_values = []

    for iunitdur, ipercent in itertools.product(range(len(unit_dur_list)), range(len(rep_percentage_list))):
        
        unitdur = unit_dur_list[iunitdur]
        percentage = rep_percentage_list[ipercent]
        stim_code = (iunitdur + 1) * 100 + (ipercent + 1)

        num_examples = n_percentage_zero if percentage == 0 else n_rest
        expected_response = 0 if percentage == 0 else 1

        for _ in range(num_examples):
            table_values.append([unitdur, percentage, stim_code, expected_response])

        ntrials = len(table_values)

    return table_values, ntrials


#=====================
#GET THE DATA FRAME
#====================
def get_df(table_name, table_dir):
    
    table_for_block = op.join(table_dir, table_name)
    df = pd.read_csv(table_for_block, sep = '\t')
    nTrials = len(df)
    return df, nTrials

#=====================
#PSEUDORANDOMIZATION
#=====================
# Function to check if any value occurs more than three times consecutively
def check_consecutive_occurrences(arr):
    count = 1
    for i in range(1, len(arr)):
        if arr[i] == arr[i-1]:
            count += 1
            if count > 3:
                return False
        else:
            count = 1
    return True


def pseudorandomize_and_save_df(df, which_block, exp_info, table_dir):
    # pseudo randomize the data frame for each individual
    # condition: any percentage value should not occur more than three times consecutively
    # shuffle dataframe rows until the condition is met
    while True:
        df_shuffled = df.sample(frac=1).reset_index(drop=True)  # Shuffle rows
        if check_consecutive_occurrences(df_shuffled['percentage']):
            break

    # save this shuffled table immediately before you forget
    shuffled_df_filename = 'detection_experiment_block_' + str(which_block) + '_pid_' + str(exp_info['participant_id']) + '_randomized_table.tsv'
    table_path = table_dir + '/participant_specific_tables/' + shuffled_df_filename
    df_shuffled.to_csv(table_path, sep='\t', index=False)
    return df_shuffled




#=====================
#SAVE OUPUT DATA FRAME
#====================
def save_output_df(output, experiment_mark, which_block, params):
    file_name = 'block_no_'+str(which_block)+ '_' + experiment_mark
    output_data_directory = op.join(params.data_dir, file_name)
    output.to_csv(output_data_directory, sep='\t', index=False)
