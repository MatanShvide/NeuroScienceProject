import mne
import os
import numpy as np
import matplotlib.pyplot as plt

#raw = mne.io.read_raw_brainvision('sub100_rt_TEP.vhdr') #extract data from files
#data = raw.get_data() #create 65 row matrix with ~7200000. Row = brain area, Column = 1 ms

def draw_all(data, indices, name, static_plot):
    for i in range(len(data)):#data.shape[0]):
        if i not in static_plot:
            continue
        # create a new directory for this row
        dirname = f'Electrode_{i}' + '_' + name
        os.makedirs(dirname, exist_ok=True)

        # plot the entire row and save it
        plt.plot(data[i])
        plt.title(f'Electrode {i}')
        plt.xlabel('ms/10')
        plt.ylabel('V')
        for index in range(len(indices)):
            plt.scatter(indices[index][0], data[i][indices[index][1]], color='red')
            plt.scatter(indices[index][0], data[i][indices[index][1]], color='red')
        plt.savefig(os.path.join(dirname, 'full_row.png'))
        plt.close()

        # plot the segment 688000-1290000 and save it
        plt.plot(data[i, indices[0][0]:indices[-1][-1]])
        plt.title(f'Electrode {i}, Indices' + str(indices[0][0]) + ' - ' + str(indices[-1][-1]) + '. Total ' + str((indices[-1][-1]-indices[0][0])/1000) + ' seconds')
        plt.xlabel('ms/10')
        plt.ylabel('V')
        for index in range(len(indices)):
            plt.scatter(indices[index][0] - indices[0][0], data[i][indices[index][1]], color='red')
            plt.scatter(indices[index][1] - indices[0][0], data[i][indices[index][1]], color='red')
        plt.savefig(os.path.join(dirname, 'All pulses.png'))
        plt.close()

        # plot all pulses
        for j in range(len(indices)):
            a = indices[j][0] - 40
            plt.plot(data[i, a:(a + 100)])
            plt.title(f'Electrode {i + 1}, Pulse' + str(j) + '   ' + str(a) + ' - ' + str(a+100) + '. Total 10 ms')
            plt.xlabel('ms/10')
            plt.ylabel('V')
            plt.savefig(os.path.join(dirname, 'pulse' + str(j) + '.png'))
            plt.close()

