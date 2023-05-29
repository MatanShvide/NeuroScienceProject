import mne
import os
import numpy as np
import matplotlib.pyplot as plt

raw = mne.io.read_raw_brainvision('sub100_rt_TEP.vhdr') #extract data from files
data = raw.get_data() #create 65 row matrix with ~7200000. Row = brain area, Column = 1 ms

for i in range(data.shape[0]):
#i=0
#if i==0:
    # create a new directory for this row
    dirname = f'row_{i+1}'
    os.makedirs(dirname, exist_ok=True)

    # plot the entire row and save it
    plt.plot(data[i])
    plt.title(f'Row {i+1}')
    plt.savefig(os.path.join(dirname, 'full_row.png'))
    plt.close()

    # plot the segment 688000-1290000 and save it
    plt.plot(data[i, 688000:1290000])
    plt.title(f'Row {i+1}, Indices 688000-1290000')
    plt.savefig(os.path.join(dirname, 'segment1.png'))
    plt.close()

    begin = [688900, 715201, 749700, 784228, 813901, 846824, 873159, 902116, 936167, 968944, 1003197, 1034649, 1059836,
         1093153, 1127244, 1158911, 1191250, 1223425, 1252195, 1283406]
    # plot all pulses
    for j in range(20):
        a = begin[j]
        plt.plot(data[i, a:(a + 30)])
        plt.title(f'Row {i + 1}, Pulse' + str(j+1))
        plt.savefig(os.path.join(dirname, 'pulse' + str(j) + '.png'))
        plt.close()

