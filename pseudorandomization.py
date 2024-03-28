    #=====================
    #PSEUDORANDOMIZATION
    #=====================
    # condition: any value should not occur more than three times consecutively
# shuffle dataframe rows until the condition is met
while True:
    df_shuffled = table_values.sample(frac=1).reset_index(drop=True)  # Shuffle rows
    if check_consecutive_occurrences(df_shuffled['percentage']):
        break

# Save the shuffled DataFrame as a TSV file

table_path = os.path.join(table_dir, tsv_filename)
df_shuffled.to_csv(table_path, sep='\t', index=False)