import pytest
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.base import TimeSeries
from pynwb.file import ProcessingModule
from pathlib import Path
from hdmf.common.table import VectorData
from ndx_events import NdxEventsNWBFile, EventsTable, TimestampVectorData, CategoricalVectorData, MeaningsTable
from unicodedata import category

from ndx_wearables import WearableDevice, WearableTimeSeries, WearableEvents, PhysiologicalMeasure


nwbfile = NdxEventsNWBFile(
    session_description="Example wearables study session",
    identifier='TEST_WEARABLES',
    session_start_time=datetime.now(pytz.timezone('America/Chicago')),
)

# generate fake wearables data
timestamps = np.arange(0, 3600, 30)
np.random.seed(0)
wearable_values = np.random.random(size=(120, 2))

# create processing module
wearables = ProcessingModule(
    name="wearables",
    description="Wearables data",
)

modality = PhysiologicalMeasure(
    name="TestMeasure",
)

# create wearables device
device = WearableDevice(name="TestDevice", description="test", location="arm", manufacturer="test")
nwbfile.add_device(device)

# Build out a meanings table to use in the events file
ts = WearableTimeSeries(
    name=f"{device.name}_TestTimeseries",
    data=wearable_values,
    timestamps=timestamps,
    description="test",
    unit="unit",
    wearable_device=device,
)

nwbfile.add_processing_module(wearables)

wearables.add([modality])

added_ts = modality.add_wearable_time_series(ts)

# add wearables objects to processing module
tmp_path = Path(r"./examples")
file_path = tmp_path / "physio_measure_demo.nwb"
with NWBHDF5IO(file_path, 'w') as io:
    io.write(nwbfile)
