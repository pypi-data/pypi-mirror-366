from pynwb.spec import NWBGroupSpec

def make_met_stage():
    met_series = NWBGroupSpec(
        doc='Stores metabolic equivalent (MET) values over time.',
        neurodata_type_def='MetSeries',
        neurodata_type_inc='WearableTimeSeries'
    )
    return met_series
