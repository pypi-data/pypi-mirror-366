from pynwb.spec import NWBGroupSpec, NWBDatasetSpec

def make_sleep_stage():
    sleep_stage_series = NWBGroupSpec(
        doc='Stores sleep stages as raw strings over time.',
        datasets=[
            NWBDatasetSpec(
                name='data',
                dtype='text',
                doc='Sleep stage labels'
            )
        ],
        neurodata_type_def='SleepStageSeries',
        neurodata_type_inc='TimeSeries',
    )
        
    return sleep_stage_series
