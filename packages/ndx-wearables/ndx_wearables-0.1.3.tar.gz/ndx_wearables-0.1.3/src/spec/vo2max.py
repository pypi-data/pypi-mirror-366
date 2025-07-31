from pynwb.spec import NWBGroupSpec, NWBAttributeSpec


def make_vo2max_stage():
    vo2max_series = NWBGroupSpec(
        doc='Stores Vo2 max values as raw strings over time.',
        neurodata_type_def='VO2maxSeries',
        neurodata_type_inc='WearableTimeSeries',
        attributes=[
            NWBAttributeSpec(
                name="algorithm", doc="Algorithm used to extract data from raw sensor readings", dtype="text", required=True
            )
        ],
    )
        
    return vo2max_series