
from pynwb.spec import NWBGroupSpec, NWBDatasetSpec, NWBAttributeSpec

def make_hrv_stage():
    hrv_series = NWBGroupSpec(
        doc='Stores HRV values as strings over time.',
        neurodata_type_def='HRVSeries',
        neurodata_type_inc='WearableTimeSeries',
        attributes=[
            NWBAttributeSpec(
                name="algorithm", doc="Algorithm used to extract data from raw sensor readings", dtype="text", required=True
            )
        ],
    )

    return hrv_series 


