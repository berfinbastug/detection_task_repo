import itertools
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
