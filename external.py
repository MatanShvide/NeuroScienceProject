import mne
from implement_interpolation import *

raw = mne.io.read_raw_brainvision('sub100_rt_TEP.vhdr')
events_from_annot, event_dict = mne.events_from_annotations(raw)
event_map = {'stim': 10002}
obj = mne.Epochs(raw, events_from_annot,baseline = (-0.2,-0.01), tmin=-0.2, tmax=0.3, event_id=event_map, preload=True,reject = None,detrend=None)

new_raw_mat = tms_pulse_interpolation(raw, find_events=True, events_to_interpolate= [10002], interpolation_type="simple")
new_epoch_mat = tms_pulse_interpolation(obj, interpolation_type="simple", find_events=False)
