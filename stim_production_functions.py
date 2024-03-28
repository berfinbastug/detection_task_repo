# here my aim is to transform an existing matlab function into a python code

#=====================
#IMPORT NECESSARY LIBRARIES
#=====================

import numpy as np
import itertools
import stimulus_params
import copy

#=====================
#FUNCTION NUMBER 1
#=====================
# this one is a separate function normally but I embedded it here I don't know whether I am doing it right
def psyramp(x, rtime, fs):

    # rtime in seconds
    lt = len(x)
    tr = np.arange(0, rtime-1/fs, 1/fs)
    lr = len(tr)
    rampup = ((np.cos(2 * np.pi * tr / rtime / 2 + np.pi) + 1) / 2) ** 2
    rampdown = ((np.cos(2 * np.pi * tr / rtime / 2) + 1) / 2) ** 2
    xr = x.copy()
    xr[:lr] = rampup * x[:lr]
    xr[lt - lr:lt] = rampdown * x[lt - lr:lt]
    return xr

#=====================
#FUNCTION NUMBER 2
#=====================
deepCopysP = copy.deepcopy(stimulus_params.sP_default)

# Define the main function with optional parameters (sP is set to None by default)
def gencloudcoherence(sP=deepCopysP, change_dict = None):
    
    # Set the parameters with default values 
    # print(change_dict)
    if change_dict is not None:
        # let's find out the things that have to change
        params2change = change_dict.keys()
        
        for param2change in params2change:
            sP[param2change] = change_dict[param2change]


    # deal with random number generator
    # is this really working?
    if sP['seed'] is not None:
        np.random.seed(sP['seed'])
    else:
        np.random.seed()
        sP['seed'] = np.random.get_state()[1][0]

    # compute lower edges of the grid
    ok = 0
    freqgrid = []
    freqgrid.append(sP['lowf'])
    idx = 0

    while not ok:
        zfreq = freqgrid[idx] * 2 ** sP['fstep']  # generating logarithmic frequency grid, steps are in octave
        if zfreq > sP['highf']:
            ok = 1
        else:
            idx += 1
            freqgrid.append(zfreq)

    # create a time grid for one repeat
    timegrid = np.arange(0, sP['unitdur']-sP['timestep'] + 0.00001, sP['timestep'])

    # initialization
    nfsteps = len(freqgrid)
    ntsteps = len(timegrid)

    # create random perturbations for frequency and time
    fnorm = np.random.rand(nfsteps, ntsteps)  # [0, 1)
    tnorm = np.random.rand(nfsteps, ntsteps)  # [0, 1)

    # now build the actual frequency and time matrices
    bigf = np.tile(np.array(freqgrid).reshape(-1, 1), (1, ntsteps))  # nominal values
    zf = 2 ** (np.log2(bigf) + fnorm * sP['fstep'])  # perturbed values
    bigt = np.tile(timegrid, (nfsteps, 1))  # nominal values
    zt = bigt + tnorm * sP['timestep']  # perturbed values

    # deal with the repeating percentage of the tones
    ntones = bigf.size
    if (sP['percentage'] == 0):
        nreptones = 0
        nnewtones = ntones - nreptones
    elif (sP['percentage'] == 1):
        nreptones = ntones
        nnewtones = ntones - nreptones
    else:
        nreptones = int(np.ceil(ntones * sP['percentage']))
        nnewtones = ntones - nreptones

    # who are the lucky few, select repeated and new tones
    idxdraw = np.random.permutation(ntones)
    idxreptones = idxdraw[:nreptones]
    idxnewtones = idxdraw[nreptones:]

    r_rep, c_rep = np.unravel_index(idxreptones, (nfsteps, ntsteps), 'C')
    r_new, c_new = np.unravel_index(idxnewtones, (nfsteps, ntsteps), 'C')
    
    bigzf = np.empty((nfsteps, 0))  # Initialize an empty array with the appropriate shape
    bigzt = np.empty((nfsteps, 0))  # Initialize an empty array with the appropriate shape

    for idelay in range(1, sP['nrep'] + 1):
        
        # create new frequency and time matrices
        newzf = zf.copy()  # create a copy of the frequency matrix
        newzt = zt.copy()

        # create new perturbation matrices
        newfnorm = np.random.rand(nfsteps, ntsteps)
        newtnorm = np.random.rand(nfsteps, ntsteps)

        # repeat the matrices
        zf[r_new, c_new] = 2 ** (np.log2(bigf[r_new, c_new]) + newfnorm[r_new, c_new] * sP['fstep'])
        zt[r_new, c_new] = bigt[r_new, c_new] + newtnorm[r_new, c_new] * sP['timestep']
        bigzf = np.concatenate((bigzf, zf), axis = 1)

        x = zt + (idelay - 1) * sP['unitdur']
        bigzt = np.concatenate((bigzt, x), axis = 1)


    # generate all tones
    tx = np.arange(0, sP['tonedur'], 1 / sP['fs'])  # support for one tone
    bigx = np.zeros(int(np.ceil((sP['unitdur'] * sP['nrep'] + sP['tonedur']) * sP['fs'])))  # the full repetition


    for itstep in range(bigzt.shape[1]):
        
        for ifstep in range(bigzf.shape[0]):
            
            tmp_tone = np.sin(2 * np.pi * tx * bigzf[ifstep, itstep])
            xtone = psyramp(tmp_tone, sP['rtime'], sP['fs'])
            
            # insert spectral shape here if needed
            istart = int(round(bigzt[ifstep, itstep] * sP['fs']))  # we round but no start at idx=0
            iend = istart + len(xtone)
            bigx[istart:iend] += xtone

            # Debugging: Print the indices and lengths
            # print("istart:", istart)
            # print("iend:", iend)
            # print("len(xtone):", len(xtone))

    
    # Normalization. Not trivial, as we want to balance loudness across freq conditions?
    x = bigx/20

    if np.max(np.abs(x)) > 0.999:
        raise ValueError('Clipped!')

    # do a bit of zero-padding
    zpad = np.zeros(int(0.2 * sP['fs']))
    y = np.concatenate((zpad, x, zpad), axis=0)

    return y, sP


def generate_baseline_table(unit_dur_list, rep_percentage_list):
    # first, generate bunch of lists
    table_values = []

    for iunitdur, ipercent in itertools.product(range(len(unit_dur_list)), range(len(rep_percentage_list))):
        
        unitdur = unit_dur_list[iunitdur]
        percentage = rep_percentage_list[ipercent]
        stim_code = (iunitdur + 1) * 100 + (ipercent + 1)

        num_examples = 90 if percentage == 0 else 10
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


