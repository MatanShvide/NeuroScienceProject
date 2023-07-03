from implement_interpolation import *

raw = mne.io.read_raw_brainvision('Data/sub_100/EEG/sub100_rt_TEP.vhdr')
obj = mne.make_fixed_length_epochs(raw)
#new_raw = tms_pulse_interpolation(raw, 'n', [0, 45, 0])
new_raw_mat = tms_pulse_interpolation(raw, 4, [4, 15, 21])
new_epoch_mat = tms_pulse_interpolation(obj, 'm', [68, 17], [71, 128])






