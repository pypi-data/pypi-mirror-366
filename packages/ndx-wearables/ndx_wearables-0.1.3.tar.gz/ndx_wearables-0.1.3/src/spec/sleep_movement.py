from pynwb.spec import NWBGroupSpec


def make_sleep_movement_stage():
    sleep_movement_series = NWBGroupSpec(
        doc='Captures movement intensity or frequency during sleep.',
        neurodata_type_def='SleepMovementSeries',
        neurodata_type_inc='WearableTimeSeries'
    )
    return sleep_movement_series
