import mne
import numpy as np

import draw_all
from draw_all import *


def get_peak(mat):
    max_mat = np.amax(mat, axis=1)
    min_mat = np.amin(mat, axis=1)
    peaks = (max_mat + np.abs(min_mat)) / 7
    return peaks


def find_abnormalities(diffs, peak):
    low_inds = np.where(diffs > peak)
    high_inds = np.where(diffs < (-peak))
    return (high_inds, low_inds)


def group_indices(indices, freq):
    high_inds = indices[0][0]
    low_inds = indices[1][0]
    pulses_lst = [[]]  # initiate grouped abnormal indices
    group_first_by_low(low_inds, pulses_lst, freq)
    add_high_to_groups(high_inds, pulses_lst, freq)
    return pulses_lst


def group_first_by_low(low_inds, pulses_lst, freq):  # creates a nested list for each suspected pulse
    cnt = 0
    for i in range(len(low_inds)):  # Loop to group values to pulses
        pulses_lst[cnt].append(low_inds[i])
        try:  # avoid error incase we reached end of list indices
            if abs(low_inds[i] - low_inds[i + 1]) > freq:  # If next index is more than 3 ms apart - NOT the same pulse
                cnt += 1
                pulses_lst.append([])  # Add another row for the next pulse of this area
        except IndexError:
            cnt += 1
            pass
    return


def add_high_to_groups(high_inds, pulses_lst, freq):
    cnt = 0
    for i in range(len(high_inds)):  # Loop to group values to pulses
        # Row already created for the abnormal high values - we will append the low values to the matching pulse
        try:  # avoid error incase we reached end of list indices
            pulses_lst[cnt].append(high_inds[i])  # Append index to pulse
            if abs(high_inds[i] - high_inds[
                i + 1]) > freq:  # If next index is more than 3 ms apart - NOT the same pulse
                cnt += 1
        except IndexError:
            cnt += 1
            pass
    return


def sort_pulses_for_region(pulses_lst):
    for i in range(len(pulses_lst)):
        pulses_lst[i] = np.sort(pulses_lst[i])


def check_shape(row, pulses_lst, peak):
    final_array = []
    for i in range(len(pulses_lst)):
        if len(pulses_lst[i]) == 0:
            continue
        values = row[pulses_lst[i]]
        inds = [k for k in range(max(0, np.amin(pulses_lst[i] - 10)), min(len(row), np.amax(pulses_lst[i] + 10)))]
        med = np.median(row[inds])
        if np.amin(values) < med - peak / 3 and np.amax(values) > med + peak / 3:
            final_array.append(pulses_lst[i].tolist())
    return final_array


def find_range(logs, rows, pulses):  # take average of all indices and create a 2.5 ms section
    result = []
    for i in range(pulses):
        min_sum = 0
        max_sum = 0
        cnt = 0
        for j in range(rows):
            try:
                max_sum += logs['Electrode ' + str(j)]['Indices'][i][-1]
                min_sum += logs['Electrode ' + str(j)]['Indices'][i][0]
            except IndexError:
                cnt += 1
                logs['Errors'].append("Error in row " + str(j) + " In pulse " + str(i))
        max_avg = max_sum // (rows - cnt)
        min_avg = min_sum // (rows - cnt)
        diff = max_avg - min_avg
        extension = (20 - diff) // 2
        result.append([min_avg - extension, max_avg + extension])
    return result


def get_pulses(mat, max_val):
    logs = {'Errors': [], 'General Info': {}}
    diffs = np.diff(mat)
    peaks = get_peak(mat)
    pulses = 1
    if np.amax(peaks) < 0.005:
        logs['Errors'].append("No pulses in this segment")
        pulses = 0
        return logs
    for i in range(len(mat)):  # for each electrode signal
        if pulses == 1:
            peak = peaks[i]  # get_peak(max_mat[i], min_mat[i])  #determine required amplitude
            logs['Electrode ' + str(i)] = {'Amplitude': peak}
            indices = find_abnormalities(diffs[i], peak)  # find abnormal indices by peak
            pulses_lst = group_indices(indices, 6)  # group abnormal indices by adjacency
            sort_pulses_for_region(pulses_lst)  # sort indices
            final_array = check_shape(mat[i], pulses_lst, peak)  # check pattern of pulses contains min&max values
            logs['Electrode ' + str(i)]['Number of pulses'] = len(final_array)
            logs['Electrode ' + str(i)]['Indices'] = final_array
        """if max_val != 20:  # if max val isn't default value, run same process for peak = max_value
            max_val_peaks_indices = find_abnormalities(diffs[i], max_val)  # find abnormal indices by max value
            max_vals_peaks_lst = group_indices(max_val_peaks_indices, 6)  # group abnormal indices by adjacency
            sort_pulses_for_region(max_vals_peaks_lst)  # sort indices
            if pulses == 1:  # if there are TMS pulses, remove TMS pulses from list of non-TMS pulses larger than max_value
                indices_set = set(final_array)
                peaks_array = [x for x in max_vals_peaks_lst if x not in indices_set]
                for peak in peaks_array:  # find max absolute value for each non-TMS peak
                    start_indice = peak[0]
                    end_indice = peak[1]
                    max_high = np.amax(mat[start_indice], mat[end_indice])
                    max_low = np.amin(mat[start_indice], mat[end_indice])
                    if max_high > -max_low:
                        peak.append(max_high)
                    else:
                        peak.append(max_low)
                logs['Electrode ' + str(i)]['non-TMS pulse peaks'] = peaks_array"""
    arr = np.empty(65)
    for i in range(len(mat)):
        arr[i] = logs['Electrode ' + str(i)]['Number of pulses']
    most_common_value = np.argmax(np.bincount(arr.astype(int)))
    lst = find_range(logs, len(mat), most_common_value)  # determine final locations of pulses
    logs['General Info']["Indices to interpolate"] = lst
    return logs
