import pytz
from datetime import datetime
from pynwb.file import ProcessingModule
from ndx_events import NdxEventsNWBFile
from ndx_wearables import WearableDevice


def make_wearables_nwbfile(identifier=None):
    now = datetime.now(pytz.timezone('America/Chicago'))
    identifier = identifier if identifier else 'TEST_WEARABLES_'+now.strftime("%H%M%S")
    nwbfile = NdxEventsNWBFile(
        session_description="Example wearables study session created at "+now.strftime("%H%M%S"),
        identifier=identifier,
        session_start_time=datetime.now(pytz.timezone('America/Chicago')),
    )

    # create processing module
    wearables_module = ProcessingModule(
        name="wearables",
        description="Wearables data",
    )

    nwbfile.add_processing_module(wearables_module)
    return nwbfile

def add_wearables_device(nwbfile):
    # create wearables device
    device = WearableDevice(name="test_wearable_device", description="test", location="arm", manufacturer="test")
    nwbfile.add_device(device)

    return nwbfile, device