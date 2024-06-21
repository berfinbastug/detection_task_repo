import os

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


def shuffled_df(df, table_dir, participant_id, which_block):

    #PSEUDORANDOMIZATION
    # condition: any value (percentage) should not occur more than three times consecutively
    # shuffle dataframe rows until the condition is met
    while True:
        df_shuffled = df.sample(frac=1).reset_index(drop=True)  # Shuffle rows
        if check_consecutive_occurrences(df_shuffled['percentage']):
            break

    # Save the shuffled DataFrame as a TSV file
    table_name = 'detection_experiment_participant_id_'+ str(participant_id) + '_randomized_block_' + str(which_block) + '_table.tsv'
    #print(table_name)
    table_path = os.path.join(table_dir, table_name)
    #print(table_path)
    df_shuffled.to_csv(table_path, sep='\t', index=False)

    return df_shuffled