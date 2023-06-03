import mne
import numpy as np

def get_peak(mat):
    max_mat = np.amax(mat, axis=1)
    min_mat = np.amin(mat, axis=1)
    peaks = (max_mat + np.abs(min_mat)) / 7
    return peaks


def find_abnormalities(diffs, peak, j):
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


def check_shape(row, pulses_lst, peak, j):
    final_array = []
    for i in range(len(pulses_lst)):
        if len(pulses_lst[i]) == 0:
            continue
        values = row[pulses_lst[i]]
        inds = [k for k in range(np.amin(pulses_lst[i] - 10), np.amax(pulses_lst[i] + 10))]
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
                max_sum += logs['Region ' + str(j + 1)]['Indices'][i][-1]
                min_sum += logs['Region ' + str(j + 1)]['Indices'][i][0]
            except IndexError:
                cnt += 1
                logs['Errors'].append("Error in row " + str(j) + " In pulse " + str(i))
        max_avg = max_sum // (rows - cnt)
        min_avg = min_sum // (rows - cnt)
        diff = max_avg - min_avg
        extension = (20 - diff) // 2
        result.append([min_avg - extension, max_avg + extension])
    return result


def get_interpolation(raw):
    logs = {}
    logs['Errors'] = []
    logs['General Info'] = {}
    mat = raw.get_data()  # create 65 row matrix with ~7200000. Row = brain area, Column = 0.1 ms
    diffs = np.diff(mat)
    peaks = get_peak(mat)
    for i in range(len(mat)):  # for each region
        peak = peaks[i]  # get_peak(max_mat[i], min_mat[i])  #determine required amplitude
        logs['Region ' + str(i + 1)] = {'Amplitude': peak}
        indices = find_abnormalities(diffs[i], peak, i)  # find abnormal indices
        pulses_lst = group_indices(indices, 6)  # group abnormal indices by adjacency
        sort_pulses_for_region(pulses_lst)  # sort indices
        final_array = check_shape(mat[i], pulses_lst, peak, i)  # check pattern of pulses contains min&max values
        logs['Region ' + str(i + 1)]['Number of pulses'] = len(final_array)
        logs['Region ' + str(i + 1)]['Indices'] = final_array
    lst = find_range(logs, len(mat), logs['Region 1']['Number of pulses'])  # determine final locations of pulses
    logs['General Info']["Indices to interpolate"] = lst
    return logs


file = 'Data/sub_100/EEG/sub100_rt_TEP'
raw = mne.io.read_raw_brainvision(file + '.vhdr')  # extract data from files
logs = get_interpolation(raw)
print(logs['General Info']["Indices to interpolate"])
print(len(logs['General Info']["Indices to interpolate"]))
print(logs['Errors'])
