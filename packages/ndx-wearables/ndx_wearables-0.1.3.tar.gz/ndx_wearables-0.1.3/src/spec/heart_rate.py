from pynwb.spec import NWBGroupSpec

def make_heart_rate_stage():
    heart_rate_series = NWBGroupSpec(
        doc='Stores heart rate.',
        neurodata_type_def='HeartRateSeries',
        neurodata_type_inc='WearableTimeSeries'
    )
    return heart_rate_series