import pytz
from datetime import datetime
from pynwb import NWBHDF5IO, NWBFile
from pynwb.file import Subject

from ndx_wearables.wearables_classes import WearableDevice

from tests import make_wearables_nwbfile
from tests.test_hrv_extension import add_hrv_data
from tests.test_vo2max_extension import add_vo2max_data
from tests.test_met_extension import add_met_data
from tests.test_activityclass_extension import add_activityclass_data
from tests.test_sleepmovement_extension import add_sleepmovement_data
from tests.test_blood_oxygen_extension import add_blood_oxygen_data
from tests.test_heart_rate_extension import add_heart_rate_data
from tests.test_sleepphase_extension import add_sleepphase_data
from tests.test_stepcount_extension import add_stepcount_data

# List of all modality specific build functions. Add your mode functions here to register them in the full demo NWB
# Each of these functions should take a pre-built NWB file, and add some synthetic data for the modality in question
MODALITY_BUILDERS = [
    add_hrv_data,
    add_heart_rate_data,
    add_vo2max_data,
    add_met_data,
    add_activityclass_data,
    add_sleepmovement_data,
    add_sleepphase_data,
    add_blood_oxygen_data,
    add_stepcount_data,
]

RELEASE = 'pre-release-0-1'
IDENTIFIER = '{}_{}'
subject = f'synthetic-{RELEASE}'
OUTPUT_PATH = fr'.\000207\sub-{subject}\sub-{subject}.nwb'

now = datetime.now(pytz.timezone('America/Chicago'))
today = now.strftime("%Y-%m-%d")

def main():
    nwbfile = make_wearables_nwbfile(identifier=IDENTIFIER.format(RELEASE, today))
    subj = Subject(
        age='P0D',
        description='Nonexistent subject for a synthetic data example',
        subject_id=subject,
        species='Homo sapiens',
        sex='O'
    )
    nwbfile.subject = subj

    watch = WearableDevice(
        name="ExampleWatch",
        description="Example device to demonstrate how data is stored by NDX-Wearables",
        location="Left Wrist",
        manufacturer="Test Industries Inc"
    )
    nwbfile.add_device(watch)

    ring = WearableDevice(
        name="ExampleRing",
        description="Example device to demonstrate how data is stored by NDX-Wearables",
        location="Right ring finger",
        manufacturer="Examplon LLC"
    )
    nwbfile.add_device(ring)

    # Add all the available modalities for one of the two devices to ensure complete coverage in example file
    for mode_build in MODALITY_BUILDERS:
        nwbfile = mode_build(nwbfile, watch)

    # # Add a few of the available modalities for the other device to demonstrate multi-device capabilities
    # for mode_build in MODALITY_BUILDERS[::2]:
    #     nwbfile = mode_build(nwbfile, ring)

    with NWBHDF5IO(OUTPUT_PATH.format(today), mode='w') as io:
        io.write(nwbfile)


if __name__ == "__main__":
    main()