import mne
import os
import numpy as np
import matplotlib.pyplot as plt

#raw = mne.io.read_raw_brainvision('sub100_rt_TEP.vhdr') #extract data from files
#data = raw.get_data() #create 65 row matrix with ~7200000. Row = brain area, Column = 1 ms

def draw_all(data, indices):
    for i in range(6):#data.shape[0]):
        # create a new directory for this row
        dirname = f'row_{i+1}'
        os.makedirs(dirname, exist_ok=True)

        # plot the entire row and save it
        plt.plot(data[i])
        plt.title(f'Row {i+1}')
        plt.savefig(os.path.join(dirname, 'full_row.png'))
        plt.close()

        # plot the segment 688000-1290000 and save it
        plt.plot(data[i, indices[0][0]:indices[-1][-1]])
        plt.title(f'Row {i+1}, Indices' + str(indices[0][0]) + ' - ' + str(indices[-1][-1]))
        plt.savefig(os.path.join(dirname, 'All pulses.png'))
        plt.close()

        # plot all pulses
        for j in range(len(indices)):
            a = indices[j][0] - 5
            plt.plot(data[i, a:(a + 30)])
            plt.title(f'Row {i + 1}, Pulse' + str(j+1) + '   ' + str(a) + ' - ' + str(a+30))
            plt.savefig(os.path.join(dirname, 'pulse' + str(j) + '.png'))
            plt.close()

