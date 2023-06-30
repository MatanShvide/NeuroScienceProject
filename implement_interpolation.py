import mne
import numpy as np
from scipy import interpolate
from get_pulses import *
import matplotlib.pyplot as plt
import random
from draw_all import *


def check_interpolation(inter_func, xaxis, yaxis, row):
    # returns the avg. distance between the interpolation value and original value
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
            xaxis = xaxis[:index] + xaxis[index + 1001:]
            yaxis = yaxis[:index] + yaxis[index + 1001:]
    x = np.arange(0, len(row))
    interpolated_row = inter_func(x)
    for x in exam_regions:
        avg += abs(interpolated_row[x] - row[x])
    print("avg. distace in exam regions is " + str(avg / len(exam_regions)))
    return


def interpolation(xaxis, yaxis, inter_xaxis, row):
    # returns a new matrix with the values created by the interpolation
    inter_func = interpolate.interp1d(xaxis, yaxis, kind='cubic')
    interpolated_row = inter_func(inter_xaxis)
    # check_interpolation(inter_func, xaxis, yaxis, row)
    return interpolated_row


def print_output_log(output_log):
    # prints input log
    # returns none
    print("Tests found " + str(output_log["sum_of_peaks"]) + " indications for irregular signals in all channels")
    print("In every channel, we found " + str(output_log["artifacts_count"]) + " tms pulse artifacts")
    for channel in range(1, len()):
        key = "Region " + str(channel)
        if len(output_log[key][1]) != 0:
            print("\t " + len(output_log[key][1]) + " irregular activity that doesn't match the tms pulse artifact were found in channel " + str(
                channel))
            print("\t locations: " + input[key][1])
        print("")  # deviation from events
    return


def interpolation_axises(row, indices):
    xaxis = [i for i in range(0, indices[0][0] - 4)]
    inter_xaxis = []
    for index in range(len(indices)):
        try:
            inter_xaxis += [i for i in range(indices[index][0] - 4, indices[index][1] + 4)]
            xaxis += [i for i in range(indices[index][1] + 4, indices[index + 1][0] - 4)]
        except IndexError:
            xaxis += [i for i in range(indices[index][1] + 4, len(row))]
    yaxis = [row[i] for i in xaxis]
    return xaxis, yaxis, inter_xaxis


def implement_interpolation_raw(raw, dynamic_plot=-1, static_plot=[]):
    # Arguments: (raw object, output format - new raw object or interpolated matrix, dynamic_plot - electrode, static_plot - list of channels to plot)
    # returns a new raw object with the interpolated values
    mat = raw.get_data()
    output_log = {}
    num_of_artifacts = {}
    logs = get_pulses(mat)
    print(logs['General Info']["Indices to interpolate"])
    output_log["sum_of_peaks"] = 0
    interpolated_mat = np.copy(mat)
    for channel in range(len(mat)):  # iterating over the channels
        print(channel)
        key = "Electrode " + str(channel)
        output_log["sum_of_peaks"] += len(logs[key]["Indices"])
        xaxis, yaxis, inter_xaxis = interpolation_axises(mat[channel], logs['General Info']["Indices to interpolate"])
        inter_yaxis = interpolation(xaxis, yaxis, inter_xaxis, mat[channel])
        for x in range(len(inter_xaxis)):
            interpolated_mat[channel][inter_xaxis[x]] = inter_yaxis[x]  # changing the interpolated values in the interpolated mat
    # Create a new Raw object with the new data matrix
    info = raw.info  # Preserve the original info structure
    output = mne.io.RawArray(interpolated_mat, info)
    mat2 = output.get_data()
    #Plot
    if dynamic_plot != -1:
        plt.plot(mat2[dynamic_plot])
        plt.show()
    """if static_plot:
        draw_all(mat, logs['General Info']["Indices to interpolate"], 'Raw_before', static_plot)
        draw_all(interpolated_mat, logs['General Info']["Indices to interpolate"], 'Raw_After', static_plot)"""
    return output


def implement_interpolation_epoch(epoch, dynamic_plot=[], static_plot=[]):
    #Arguments: (epoch object, output format (currently only interpolated matrix), dynamic_plot = [segment][electode], static_plot = list of segments to plot)
    # returns an interpolated matrix
    mat = epoch.get_data()
    raw = epoch._raw
    mat_new = raw.get_data()
    output_log = {"sum_of_peaks": 0}
    interpolated_mat = np.copy(mat)
    for segment in range(len(mat)):
        logs = get_pulses(mat[segment])
        print(segment)
        if logs['Errors'] and logs['Errors'][0] == "No pulses in this segment":
            continue
        for channel in range(len(mat[segment])):  # iterating over the channels
            key = "Electrode " + str(channel)
            output_log["sum_of_peaks"] += len(logs[key]["Indices"])
            xaxis, yaxis, inter_xaxis = interpolation_axises(mat[segment][channel], logs['General Info']["Indices to interpolate"])
            inter_yaxis = interpolation(xaxis, yaxis, inter_xaxis, mat[segment][channel])
            for x in range(len(inter_xaxis)):
                interpolated_mat[segment][channel][inter_xaxis[x]] = inter_yaxis[x]  # changing the interpolated values in the interpolated mat
                mat_new[channel][segment*10000 + inter_xaxis[x]] = inter_yaxis[x]
                seg = segment
        """if static_plot != 0 and segment in static_plot:
            lst = [i for i in range(len(mat[segment]))]
            draw_all(mat[segment], logs['General Info']["Indices to interpolate"], 'Epoch_before_segment ' + str(segment), lst)
            draw_all(interpolated_mat[segment], logs['General Info']["Indices to interpolate"], 'Epoch_After_segment ' + str(segment), lst)"""
    # Create a new epoch object with the new data matrix
    output = create_new_epoch(raw, epoch, mat_new)
    mat2 = output.get_data()
    #Plot
    if dynamic_plot[0]:
        #plt.plot(mat2[dynamic_plot[0]][dynamic_plot[1]])
        plt.plot(mat2[seg][0])
        plt.show()
    return output

def create_new_epoch(raw, epoch, mat_new):
    info = raw.info
    t_min = epoch.tmin
    t_max = epoch.tmax
    events = epoch.events
    new_raw = mne.io.RawArray(mat_new, info)
    output = mne.Epochs(new_raw, events=events, tmin=t_min, tmax=t_max, baseline=None, preload=True)
    return output

def tms_pulse_interpolation(input, dynamic_plot, static_plot):
    #input - object to work on
    #output - 'n' new object or 'm' new matrix
    #plot [0/1 = n/y, segment, channel] !!For raw only channel

    if isinstance(input, mne.Epochs):
        return implement_interpolation_epoch(input, dynamic_plot, static_plot)
    if isinstance(input, mne.io.brainvision.brainvision.RawBrainVision):
        return implement_interpolation_raw(input, dynamic_plot, static_plot)
    else:
        return "Invalid Input"