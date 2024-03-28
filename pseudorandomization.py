from data_frame_functions import check_consecutive_occurrences
import experiment_params as params
import os
import pandas as pd

def shuffled_df(df, table_dir, participant_id, which_block):

    #PSEUDORANDOMIZATION
    #=====================
    # condition: any value should not occur more than three times consecutively
    # shuffle dataframe rows until the condition is met
    while True:
        df_shuffled = df.sample(frac=1).reset_index(drop=True)  # Shuffle rows
        if check_consecutive_occurrences(df_shuffled['percentage']):
            break

    # Save the shuffled DataFrame as a TSV file
    table_name = 'participant_id_'+ str(participant_id) + '_randomized_block_' + str(which_block) + '_table.tsv'
    #print(table_name)
    table_path = os.path.join(table_dir, table_name)
    #print(table_path)
    df_shuffled.to_csv(table_path, sep='\t', index=False)

    return df_shuffled