import itertools

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