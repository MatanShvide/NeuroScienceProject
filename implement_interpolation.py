import mne
import numpy as np
from scipy import interpolate
from get_pulses import *
import matplotlib.pyplot as plt
import random
from draw_all import *
#from ARExtrapolation import *

def compare_events_to_get_pulse(logs, og_mat):
    significant_diff = 50
    if len(og_mat.shape) == 3:
        get_pulses_log = {'Errors': [], 'General Info': {}}
        get_pulses_log['General Info']['Indices to interpolate'] = []
        for seg in range(len(og_mat)):
            epoch_log = get_pulses(og_mat[seg])
            get_pulses_log['General Info']['Indices to interpolate'] += epoch_log['General Info']['Indices to interpolate']
    else:
        get_pulses_log = get_pulses(og_mat)
    obj_indices = logs['General Info']['Indices to interpolate']
    get_pulses_indices = get_pulses_log['General Info']['Indices to interpolate']
    if len(obj_indices) != len(get_pulses_indices):
        print("Warning! number of pulses found  (" + str(len(get_pulses_indices)) + 
              ") is different from number of events (" + str(obj_indices) + ")")
        return False
    for i in range(len(obj_indices)):
        if abs(obj_indices[i] - get_pulses_indices[i]) > significant_diff:
            print("Warning! significant difference between detected tms pulse timestamp " + str(get_pulses_indices[i]) +
                  " and event timestamp " + str(obj_indices[i]))
    return True 

def check_interpolation(xaxis, yaxis):
    # returns the avg. distance between the interpolation value and original value
    count = 0
    exam_regions = []
    yaxis_exam_regions = []
    while count < 5:
        index = random.randrange(0, len(xaxis))
        if index + 100 >= len(xaxis) or xaxis[index + 100] - xaxis[index] != 100:
            continue
        else:
            count += 1
            exam_regions += xaxis[index:index + 101]
            yaxis_exam_regions += yaxis[index:index + 101]
            xaxis = xaxis[:index] + xaxis[index + 101:]
            yaxis = yaxis[:index] + yaxis[index + 101:]
    x = np.arange(0, len(exam_regions))
    interpolated_row = interpolation_simple(xaxis, yaxis, exam_regions)
    diff = abs(interpolated_row - yaxis_exam_regions)
    return np.mean(diff), np.std(diff), np.amax(diff), np.amin(diff)



def print_visual(og_object, inter_object, logs, slice_before, slice_after, epoch=0, channel=0):
    # Changing indices to interpolate to contain sub-lists of ranges, rather than first index of pulse.
    lst = []
    inter_indices = logs['General Info']['Indices to interpolate']
    for i in range(len(inter_indices)):
        lst.append([inter_indices[i] - slice_before, inter_indices[i] + 25 + slice_after])
    logs['General Info']['Indices to interpolate'] = lst

    if isinstance(inter_object, mne.Epochs):
        if len(logs['General Info']) == 0:
            return
        og_mat = og_object.get_data()[epoch]
        inter_mat = inter_object.get_data()[epoch]
        start_point = max(logs['General Info']['Indices to interpolate'][0][0] - 50, 0)
        end_point = min(logs['General Info']['Indices to interpolate'][0][1] + 51, len(inter_mat[0]))
    else:
        og_mat = og_object.get_data()
        inter_mat = inter_object.get_data()
        interpolation_region_num = random.randrange(0, len(logs['General Info']['Indices to interpolate']))
        start_point = max(logs['General Info']['Indices to interpolate'][interpolation_region_num][0] - 50, 0)
        end_point = min(logs['General Info']['Indices to interpolate'][interpolation_region_num][1] + 76,
                        len(inter_mat[0]))
    xaxis = [x for x in range(start_point, end_point)]
    og_yaxis = [og_mat[channel][x]*1000 for x in xaxis]
    inter_yaxis = [inter_mat[channel][x]*1000 for x in xaxis]
    xaxis = [(x / 10)- logs['General Info']['Indices to interpolate'][0][0]/10 for x in xaxis]
    plt.plot(xaxis, inter_yaxis, color='red')
    plt.plot(xaxis, og_yaxis, color='blue')
    plt.xlabel('ms')
    plt.ylabel('mV')
    if isinstance(inter_object, mne.Epochs):
        plt.title("Channel " + str(channel) + " Epoch" + str(epoch) + " Indices: " + str(start_point) + " -  " + str(
            end_point))
    else:
        plt.title("Channel " + str(channel) + " Indices: " + str(start_point) + " -  " + str(end_point))
    plt.show()


def interpolation_simple(xaxis, yaxis, inter_xaxis):
    # returns a new row with the values created by the interpolation in the inter_xaxis 
    inter_func = interpolate.Akima1DInterpolator(xaxis, yaxis)
    interpolated_val = inter_func(inter_xaxis)
    return interpolated_val


def print_output_log(logs, find_events, og_mat, raw):
    # prints input log
    # returns none
    if find_events == False:
        if compare_events_to_get_pulse(logs, og_mat): 
            print("Tests found " + str(len(logs['General Info']['Indices to interpolate'])) + " indications of TMS pulse")
    else: 
        print("Tests found " + str(len(logs['General Info']['Indices to interpolate'])) + " indications of TMS pulse")
    print("The electrode randomly chosen to be tested is " + raw.info.ch_names[logs['General Info']['exam region'][0]])
    print("Interpolation tests return average difference between original value and interpolated value of " + str(logs['General Info']['exam region'][1][0]),
          "with standard diviation of " + str(logs['General Info']['exam region'][1][1]) + ", maximal difference between values is " + str(logs['General Info']['exam region'][1][2])
           + " and minimal difference between values is " + str(logs['General Info']['exam region'][1][3]))
    return


def interpolation(row, indices, slice_before, slice_after, learn_before, learn_after, interpolation_type, test):
    # define interpolated regions and x,y axises for the interpolation function, and calls the interpolation
    # retruns the updates row with the values in tms-pulse areas replaced after interpolation
    assert interpolation_type in {"autoregressive" , "simple"} , "Interpolation can be either autoregressive or simple"
    inter_row = np.copy(row)
    xaxis = []
    inter_xaxis = []
    test_xaxis = []
    pulses = []
    for index in range(len(indices)):
        start_inter = int(indices[index] - slice_before)
        end_inter = int(indices[index] + 25 + slice_after)
        if test:
            pulses.append([start_inter, end_inter])
        if interpolation_type == "autoregressive":
            inter_vals = ARExtrapolations(row, [start_inter, end_inter] , learn_before, learn_after)
        else:    
            try:
                xaxis = []
                # adding interpolation section
                # checks if the interpolation is learning from corrupt data
                if index != 0:
                    if start_inter - learn_before < indices[index - 1] + slice_after:
                        print("learning section before indice  " + str(
                            indices[index]) + " overlaps with the previous interpolated area! Reduce your learning section")
                        print(indices[index-1])
                if index != len(indices) - 1:
                    if end_inter + learn_after > indices[index + 1] - slice_before:
                        print("learning section after indice number " + str(
                            indices[index]) + " overlaps with the next interpolated area! Reduce your learning section")
                        print(indices[index+1])
                # adding to interpolated x axis
                inter_xaxis = [i for i in range(start_inter, end_inter)]
                # adding learning section before interpolation section
                xaxis = [i for i in range(start_inter - learn_before, start_inter)]
                # adding learning section after interpolation section
                xaxis += [i for i in range(end_inter, end_inter + learn_after)]
                yaxis  = [row[x] for x in xaxis]
            except IndexError:
                print("not enough data for learning section around indice number " + str(index + 1))           
            inter_vals = interpolation_simple(xaxis , yaxis, inter_xaxis)

        for i in range(end_inter  - start_inter):
            inter_row[start_inter + i] = inter_vals[i] 
    if test:
        test_xaxis = [x for x in range(pulses[0][0])]
        for i in range(1, len(pulses)):
            test_xaxis += [x for x in range (pulses[i-1][1], pulses[i][0])]
        test_xaxis += [x for x in range(pulses[-1][1], len(row))]
        test_yaxis = [row[x] for x in test_xaxis] 
        return inter_row, check_interpolation(test_xaxis, test_yaxis)       
    return inter_row, None


def implement_interpolation_raw(raw, find_events, slice_before, slice_after, plot, learn_before, learn_after,
                                events_to_interpolate, interpolation_type):
    # returns a new raw object with the interpolated values
    mat = raw.get_data()
    if find_events:  # if user want us to find tms pulses
        logs = get_pulses(mat)
    else:  # if user wants to use mne events as indices
        logs = {'General Info': {}}
        events = mne.events_from_annotations(raw)[0]
        logs['General Info']['Indices to interpolate'] = []
        if events_to_interpolate == []:
            logs['General Info']['Indices to interpolate'] = [row[0] for row in events]
        else:
            for id in events_to_interpolate:
                logs['General Info']['Indices to interpolate'] += [row[0] for row in events if row[2] == id]
    interpolated_mat = np.copy(mat)
    test_channel = random.randrange(0, len(mat))
    for channel in range(len(mat)):  # iterating over the channels
        if channel == test_channel:
            test = True
        else:
            test = False
        inter_row, check_interpolation_res = interpolation(mat[channel], logs['General Info']['Indices to interpolate'],
                                                         slice_before, slice_after, learn_before, learn_after, interpolation_type, test)
        if test:     
            logs['General Info']['exam region'] = [test_channel, check_interpolation_res]
        interpolated_mat[channel] = inter_row # changing the interpolated values in the interpolated mat
    # Create a new Raw object with the new data matrix
    info = raw.info  # Preserve the original info structure
    if find_events:
        info.events = logs['General Info']['Indices to interpolate']
    output = mne.io.RawArray(interpolated_mat, info)
    print_output_log(logs, find_events, mat, raw)
    if plot:
        print_visual(output, raw, logs, slice_before, slice_after)

    return output


def implement_interpolation_epoch(epoch, find_events, slice_before, slice_after, plot, learn_before, learn_after,
                                  interpolation_type):
    # Modifies the data of the original Epochs object with the interpolated values
    intered_epoch = epoch.copy()
    mat = intered_epoch.get_data()
    adjusted_segments = []
    test_segment = random.randrange(0, len(mat))
    test_channel = random.randrange(0, len(mat[0]))
    gen_logs =  {'General Info': {}}
    gen_logs['General Info']['Indices to interpolate'] = []
    for segment in range(len(mat)):
        if find_events:  # If the user wants us to find TMS pulse in epoch 
            logs = get_pulses(mat[segment])
        else:  # If the user wants to use MNE events as indices
            logs = {'General Info': {}}
            logs['General Info']['Indices to interpolate'] = [int(epoch.tmin*10000*(-1))]
        gen_logs['General Info']['Indices to interpolate'] += logs['General Info']['Indices to interpolate']
        adjusted_segments.append(segment)
        for channel in range(len(mat[segment])):
            if channel == test_channel and segment == test_segment:
                test = True
            else:
                test = False
            inter_row, check_interpolation_res = interpolation(mat[segment][channel],
                                                             logs['General Info']['Indices to interpolate'],
                                                             slice_before, slice_after, learn_before, learn_after, interpolation_type, test)
            if test:     
                gen_logs['General Info']['exam region'] = [test_channel, check_interpolation_res]
            
            mat[segment][channel] = inter_row
    if plot:
        test_segment = random.choice(adjusted_segments)
        print_visual(intered_epoch, epoch, logs, slice_before, slice_after, test_segment, test_channel)
    print_output_log(gen_logs, find_events, mat, epoch)
    return intered_epoch



def tms_pulse_interpolation(input, find_events=True, slice_before=0.4, slice_after=0.9, plot=True, learn_before=10,
                            learn_after=10, events_to_interpolate=[], interpolation_type = "simple"):
    # slice_before, slice_after, learn_before and learn_after in ms
    # events to interpolate: an array of event id's that will be interpolated (when choosing to interpolate from events). default is an empty array, in this case every event will be interpolated
    # two possible types of interpolation: autoregressive or simple
    if isinstance(input, mne.Epochs):
        return implement_interpolation_epoch(input, find_events, int(slice_before * 10), int(slice_after * 10), plot,
                                             int(learn_before * 10), int(learn_after * 10), interpolation_type)
    if isinstance(input, mne.io.brainvision.brainvision.RawBrainVision):
        return implement_interpolation_raw(input, find_events, int(slice_before * 10), int(slice_after * 10), plot,
                                           int(learn_before * 10), int(learn_after * 10), events_to_interpolate, interpolation_type)
    else:
        return "Invalid Input"
    


