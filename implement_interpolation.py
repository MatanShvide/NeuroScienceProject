import mne
import numpy as np
from scipy import interpolate
from get_pulses import *
import matplotlib.pyplot as plt
import random
from draw_all import *

def print_visual(og_object, inter_object, logs, epoch = 0, channel = 0):
        if isinstance(inter_object, mne.Epochs):
            og_mat = og_object.get_data()[epoch]
            inter_mat = inter_object.get_data()[epoch]
            start_point = max(logs['General Info']["Indices to interpolate"][0][0] - 50, 0)
            end_point = min(logs['General Info']["Indices to interpolate"][0][1] + 51, len(inter_mat[0]))
        else:
            og_mat = og_object.get_data()
            inter_mat = inter_object.get_data()
            interpolation_region_num = random.randrange(0 , len(logs['General Info']["Indices to interpolate"]))
            start_point = max(logs['General Info']["Indices to interpolate"][interpolation_region_num][0] - 50, 0)
            end_point = min(logs['General Info']["Indices to interpolate"][interpolation_region_num][1] + 51, len(inter_mat[0]))
        xaxis = [x for x in range(start_point, end_point)]
        og_yaxis = [og_mat[channel][x] for x in xaxis]
        inter_yaxis = [inter_mat[channel][x] for x in xaxis]
        plt.plot(xaxis, inter_yaxis, color='red')
        plt.plot(xaxis, og_yaxis, color='blue')
        plt.xlabel('ms/10')
        plt.ylabel('V')
        if isinstance(inter_object, mne.Epochs):
            plt.title("Channel " + str(channel) + " Epoch" + str(epoch) + " Indices: " + str(start_point) + " -  " + str(end_point))
        else:
            plt.title("Channel " + str(channel) + " Indices: " + str(start_point) + " -  " + str(end_point))
        plt.show()


def check_interpolation(xaxis, yaxis):
    # returns the avg. distance between the interpolation value and original value
    count = 0
    exam_regions = []
    yaxis_exam_regions = []
    avg = 0
    while count < 5:
        index = random.randrange(0, len(xaxis))
        if index + 1000 > len(xaxis) or xaxis[index + 1000] - xaxis[index] != 1000:
            continue
        else:
            count += 1
            exam_regions += xaxis[index:index + 1001]
            yaxis_exam_regions += yaxis[index:index + 1001]
            xaxis = xaxis[:index] + xaxis[index + 1001:]
            yaxis = yaxis[:index] + yaxis[index + 1001:]
    x = np.arange(0, len(exam_regions))
    interpolated_row = interpolation(xaxis , yaxis, exam_regions)
    diff =  abs(interpolated_row - yaxis_exam_regions)
    return np.mean(diff) , np.std(diff) , np.amax(diff) , np.amin(diff) 


def interpolation(xaxis, yaxis, inter_xaxis):
    # returns a new matrix with the values created by the interpolation
    inter_func = interpolate.interp1d(xaxis, yaxis, kind='cubic')
    interpolated_row = inter_func(inter_xaxis)
    return interpolated_row


def print_output_log(logs, raw):
    # prints input log
    # returns none
    print("Tests found " + str(len(logs['General Info']['Indices to interpolate'])) + " indications of TMS pulse")
    print("The electrode randomly chosen to be tested is " + raw.info.ch_names[logs['General Info']['exam region'][0]])
    print("Interpolation tests return average difference between original value and interpolated value of " + str(logs['General Info']['exam region'][1][0]),
          " with standard diviation of " + str(logs['General Info']['exam region'][1][1]) + "maximal difference between values is " + str(logs['General Info']['exam region'][1][2])
           + " and minimal difference between values is " + str(logs['General Info']['exam region'][1][3]))
    return


def interpolation_axises(row, indices, slice_before , slice_after, log):
    # define interpolated regions and x,y axises for the interpolation function
    xaxis = [i for i in range(indices[0][0] - slice_before)]
    inter_xaxis = []
    for index in range(len(indices)):
        try:
            inter_xaxis += [i for i in range(indices[index][0] - slice_before, indices[index][1] + slice_after)]
            xaxis += [i for i in range(indices[index][1] + slice_after, indices[index + 1][0] - slice_before)]
        except IndexError:
            xaxis += [i for i in range(indices[index][1] + slice_after, len(row))]
    if 'non-TMS pulse peaks' in log:
        cont_indices = set()
        for peak in log['non-TMS pulse peaks']:
            i = peak[0]
            while i <= peak[1]:
                cont_indices.add(i)
                i += 1
        xaxis = [x for x in xaxis if x not in cont_indices]
    yaxis = [row[i] for i in xaxis]
    return xaxis, yaxis, inter_xaxis


def implement_interpolation_raw(raw, max_val, slice_before, slice_after, plot):
    # returns a new raw object with the interpolated values
    mat = raw.get_data()
    logs = get_pulses(mat, max_val)
    #print(logs['General Info']["Indices to interpolate"])
    interpolated_mat = np.copy(mat)
    test_channel = random.randrange(0, len(mat))
    for channel in range(len(mat)):  # iterating over the channels
        key = "Electrode " + str(channel)
        print(key)
        xaxis, yaxis, inter_xaxis = interpolation_axises(mat[channel], logs['General Info']["Indices to interpolate"], slice_before , slice_after, logs[key])
        inter_yaxis = interpolation(xaxis, yaxis, inter_xaxis)
        if channel == test_channel:
            logs['General Info']['exam region'] = [test_channel] + [check_interpolation(xaxis, yaxis)]
        for x in range(len(inter_xaxis)):
            interpolated_mat[channel][inter_xaxis[x]] = inter_yaxis[x]  # changing the interpolated values in the interpolated mat
    # Create a new Raw object with the new data matrix
    info = raw.info  # Preserve the original info structure
    output = mne.io.RawArray(interpolated_mat, info)
    #mat2 = output.get_data()
    print_output_log(logs, raw)
    if plot:
        print_visual(output, raw, logs)
    return output


def implement_interpolation_epoch(epoch, max_val, slice_before, slice_after, plot):
    # returns an interpolated matrix
    mat = epoch.get_data()
    raw = epoch._raw
    mat_new = raw.get_data()
    interpolated_mat = np.copy(mat)
    adjusted_segments = []
    test_segment = random.randrange(0, len(mat))
    test_channel = random.randrange(0, len(mat[0]))
    empty_segments = []
    for segment in range(len(mat)):
        logs = get_pulses(mat[segment], max_val)
        if logs['Errors'] and logs['Errors'][0] == "No pulses in this segment":
            empty_segments.append(segment)
            continue
        adjusted_segments.append(segment)
        for channel in range(len(mat[segment])):  # iterating over the channels
            key = "Electrode " + str(channel)
            xaxis, yaxis, inter_xaxis = interpolation_axises(mat[segment][channel], logs['General Info']["Indices to interpolate"], slice_before, slice_after, logs[key])
            inter_yaxis = interpolation(xaxis, yaxis, inter_xaxis)
            if segment == test_segment and channel == test_channel: # performing check_interpolation for randomly selected location
                logs['General Info']['exam region'] = [check_interpolation(xaxis, yaxis)]
                print("epoch tested:  " + str(test_segment) + " electrode tested: " + key + " average difference is " + str(logs['General Info']['exam region'][0]) )
            for x in range(len(inter_xaxis)):
                interpolated_mat[segment][channel][inter_xaxis[x]] = inter_yaxis[x]  # changing the interpolated values in the interpolated mat
                mat_new[channel][segment*10000 + inter_xaxis[x]] = inter_yaxis[x]
    output = create_new_epoch(raw, epoch, mat_new)
    #Plot
    if plot:
        test_channel = random.randrange(0, len(mat[0]))
        test_segment = random.choice(adjusted_segments)
        logs = get_pulses(mat[test_segment], max_val)
        print_visual(output, epoch, logs, test_segment, test_channel)
    #print_output_log(logs, epoch)
    return output

def create_new_epoch(raw, epoch, mat_new):
    info = raw.info
    t_min = epoch.tmin
    t_max = epoch.tmax
    events = epoch.events
    new_raw = mne.io.RawArray(mat_new, info)
    output = mne.Epochs(new_raw, events=events, tmin=t_min, tmax=t_max, baseline=None, preload=True)
    return output


def tms_pulse_interpolation(input, max_val = 20, slice_before = 4, slice_after = 4, plot = True):
    if isinstance(input, mne.Epochs):
        return implement_interpolation_epoch(input, max_val, slice_before, slice_after, plot)
    if isinstance(input, mne.io.brainvision.brainvision.RawBrainVision):
        return implement_interpolation_raw(input,  max_val, slice_before, slice_after, plot)
    else:
        return "Invalid Input"