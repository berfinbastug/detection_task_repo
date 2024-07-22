# %%
from tone_cloud_production import gencloudcoherence
from psychtoolbox import audio, PsychPortAudio

params = {
        'lowf': 200,       # lower edge of the frequency grid
        'highf': 3000,     # nominal higher edge of the frequency grid (we overshoot by at most fstep)
        'fstep': 0.4,      # size of grid cell, in octave
        'timestep': 0.05,  # in s. By default: start at any time point within the timestep
        'tonedur': 0.05,   # duration of one tone
        'unitdur': 0.4,    # how long is a repeat, in s
        'nrep': 10,        # how many repeats do we generate (warning: 1 is actually no repeat! 2 is 1+1)
        'percentage': 1,    # what is the proportion of tones repeated in each repeat
        'seed': None,      # use this if you want to regenerate the same stimulus
        'rtime': 0.025,    # rise time for individual tones
        'fs': 44100        # sampling rate
        }

ok = 0
freqgrid = []
freqgrid.append(params['lowf'])
idx = 0

while not ok:
        zfreq = freqgrid[idx] * 2 ** params['fstep']  # generating logarithmic frequency grid, steps are in octave
        if zfreq > params['highf']:
                ok = 1
        else:
                idx += 1
                freqgrid.append(zfreq)


y, sP = gencloudcoherence(params)


# %%
stream = audio.Stream(freq= 44100, channels =1)
stim = y
stream.fill_buffer(stim)
stream.start(when = 0, wait_for_start = 1)
# stream.close()

# %%
