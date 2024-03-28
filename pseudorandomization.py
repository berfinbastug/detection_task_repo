from data_frame_functions import check_consecutive_occurrences
import experiment_params as params
import os
import pandas as pd

table_dir = params.table_dir
files = os.listdir(table_dir)
# Filter out only the files with the .tsv extension
tsv_files = [file for file in files if file.endswith('.tsv')]

for itable in tsv_files:
    df_path = os.path.join(table_dir, itable)
    df = pd.read_csv(df_path, delimiter='\t')
    
    for i in range(20):
        pid = i + 1
        #=====================
        #PSEUDORANDOMIZATION
        #=====================
        # condition: any value should not occur more than three times consecutively
        # shuffle dataframe rows until the condition is met
        while True:
            df_shuffled = df.sample(frac=1).reset_index(drop=True)  # Shuffle rows
            if check_consecutive_occurrences(df_shuffled['percentage']):
                break

        # Save the shuffled DataFrame as a TSV file
        table_name = 'participantid_' + str(pid) + '_randomized_' + itable
        table_path = os.path.join(table_dir, table_name)
        df_shuffled.to_csv(table_path, sep='\t', index=False)