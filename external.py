import mne
from implement_interpolation import *

raw = mne.io.read_raw_brainvision('Data/sub_005/EEG/sub_005_rt_TEP.vhdr')
obj = mne.make_fixed_length_epochs(raw)

new_raw_mat = tms_pulse_interpolation(raw, 0.1, 4, 10)
new_epoch_mat = tms_pulse_interpolation(obj, 0.1, slice_before=6, slice_after=10)
