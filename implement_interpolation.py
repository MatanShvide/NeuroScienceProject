import mne
import numpy as np
from scipy import interpolate
from get_interpolation_improved import *
import matplotlib.pyplot as plt
import random

def check_interpolation(inter_func, xaxis , yaxis, row):
    #returns the avg. distance between the interpolation value and original value
    count = 0
    exam_regions = []
    avg = 0
    while count < 5:
        index = random.randrange(0, len(xaxis))
        if index + 1000 > len(xaxis) or xaxis[index + 1000] - xaxis[index] != 1000:
            continue
        else:
            count += 1
            exam_regions += xaxis[index:index + 1001]
            xaxis = xaxis[:index] + xaxis[index +1001:]
            yaxis = yaxis[:index] + yaxis[index +1001:]
    x = np.arange(0, len(row))
    interpolated_row = inter_func(x)
    for x in exam_regions:
        avg += abs(interpolated_row[x] - row[x])
    print("avg. distace in exam regions is " + str(avg/len(exam_regions)))
    return

def interpolation(xaxis , yaxis, inter_xaxis, row):
    # returns a new matrix with the values created by the interpolation
    inter_func = interpolate.interp1d(xaxis, yaxis, kind = 'cubic')
    interpolated_row = inter_func(inter_xaxis)
    #check_interpolation(inter_func, xaxis, yaxis, row) 
    return interpolated_row

def compare_to_events(raw ,indices ):
    # compares our tms timestamps with events recorded by the machine
    # prints avg. deviation from reported starting of tmps pulse and avg. deviation 
    # from reported ending on tmps pulse and ranges in which the deviation was significant
    events = mne.events_from_annotations(raw)


    return

def print_output_log(output_log):
    #prints input log 
    #returns none
    print("Tests found " + str(output_log["sum_of_peaks"]) + " indications for irregular signals in all channels")
    print("In every channel, we found " + str(output_log["artifacts_count"]) + " tms pulse artifacts" )
    for channel in range(1, len()):
        key = "Region " + str(channel)
        if len(output_log[key][1]) != 0 : 
            print("\t " + len(output_log[key][1]) + " irregular activity that don't match the tms pulse artifact were found in channel " + str(channel))
            print("\t locations: " + input[key][1])
        print("") #deviation from events
    return 

def interpolation_axises(row , indices):
    xaxis = [ i for i in range(indices[0][0])]
    new_xaxis = []
    for index in range(len(indices)):
        try :
            new_xaxis += [i for i in range(indices[index][0], indices[index][1] + 1)]
            xaxis += [i for i in range(indices[index][1] , indices[index + 1][0])]
        except IndexError:
            xaxis += [i for i in range(indices[index][1] , len(row))]  
    yaxis = [row[i] for i in xaxis] 
    return xaxis , yaxis , new_xaxis

def main( ): #main arguments: raw, logs, max = none, min = none
    # returns a new raw object with the interpolated values
    raw = mne.io.read_raw_brainvision('Data/sub_100/EEG/sub100_rt_TEP.vhdr')
    mat = raw.get_data()
    output_log = {}
    num_of_artifacts = {}
    logs = get_interpolation(raw)
    output_log["sum_of_peaks"] = 0
    interpolated_mat = np.copy(mat)
    for channel in range(len(mat)): #iterating over the channels
        key = "Region " + str(channel+1)
        output_log["sum_of_peaks"] += len(logs[key]["Indices"]) 
        ##output_log[key] = [passed_check , failed_check]
        # adding number of artifact in channel to dict. checks if all channels have the same number of artifacts
        ##if len(output_log[key][0]) not in num_of_artifacts:
        ##    num_of_artifacts[output_log[key][0]] = [channel]
        ##else:
        ##    num_of_artifacts[output_log[key][0]].append(channel)
        compare_to_events(raw , logs['General Info']["Indices to interpolate"])
        xaxis , yaxis , inter_xaxis = interpolation_axises(mat[channel] , logs['General Info']["Indices to interpolate"] )
        inter_yaxis = interpolation(xaxis, yaxis, inter_xaxis ,mat[channel])
        for x in range(len(inter_xaxis)):
            interpolated_mat[channel][inter_xaxis[x]] = inter_yaxis[x]  #changing the interpolated values in the interpolated mat
        #count = 0
        #avg = 0
        #for n in range(len(xaxis)):
            #i = xaxis[n]
            #avg += abs(interpolated_mat[channel][i] - mat[channel][i])
            #if mat[channel][i] != interpolated_mat[channel][i]:
                #count += 1
        #print("found " + str(count) + " different values after interpolation")
        #print("avg. difference between mats is " + str(avg/len(xaxis)))
        #if channel == 0:
        #    plt.plot( [x for x in range(len(interpolated_mat[channel]))] , interpolated_mat[channel] , label = "interpolated")
        #    plt.scatter(xaxis , yaxis , label = "original" , color = 'red')
        #    plt.legend()
        #    plt.show()

    # Create a new Raw object with the new data matrix
    info = raw.info  # Preserve the original info structure
    raw_new = mne.io.RawArray(interpolated_mat, info)
    #new_mat = raw_new.get_data()
    #plt.plot(new_mat[1])
    #plt.show()
    return raw_new






    return 

if __name__ == "__main__":
    main()