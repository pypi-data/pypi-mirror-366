from pynwb.spec import NWBGroupSpec

def make_activity_class_stage():
    activity_class_series = NWBGroupSpec(
        doc='Stores categorical labels for physical activity class over time.',
        neurodata_type_def='ActivityClassSeries',
        neurodata_type_inc='EnumTimeSeries'
    )
    return activity_class_series
