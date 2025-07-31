"""
Note, tests expect to be run from the ndc-wearables root directory
"""

import pytest
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.base import TimeSeries
from pynwb.file import ProcessingModule
from pathlib import Path

from hdmf.common.table import VectorData
from ndx_events import NdxEventsNWBFile, MeaningsTable, CategoricalVectorData
from ndx_wearables import WearableDevice, WearableTimeSeries, WearableEvents

def add_wearable_timeseries(nwbfile, device):
    # generate fake wearables data
    timestamps = np.arange(0, 3600, 30)
    np.random.seed(0)
    wearable_values = np.random.random(size=(120, 2))

    # create wearable timeseries
    ts = WearableTimeSeries(
        name="test_wearable_timeseries",
        data=wearable_values,
        timestamps=timestamps,
        unit='tests/s',
        wearable_device=device,
        algorithm='test_algorithm',
    )

    # add wearables objects to processing module
    nwbfile.processing["wearables"].add_container(ts)
    return nwbfile

def add_wearable_events(nwbfile, device):
    # Build out a meanings table to use in the events file
    test_meanings = MeaningsTable(name="test_meanings", description="test")
    test_meanings.add_row(value='a', meaning="first value entered")
    test_meanings.add_row(value='b', meaning="second value entered")
    cat_column = CategoricalVectorData(name='cat_column', description='test categories description',
                                       meanings=test_meanings)
    text_column = VectorData(
        name='text_column',
        description='test columns description',
    )

    events = WearableEvents(
        name="test_wearable_events",
        description=f"test events collected from {device.name}",
        wearable_device=device,
        columns=[cat_column, text_column],
        meanings_tables=[test_meanings],
        algorithm='test_algorithm',
    )
    events.add_row(timestamp=10.0, cat_column="a", text_column="first row text")
    events.add_row(timestamp=30.0, cat_column="b", text_column="second row text")
    events.add_row(timestamp=120.0, cat_column="a", text_column="third row text")

    nwbfile.processing["wearables"].add_container(events)
    return nwbfile

@pytest.fixture
def nwb_with_wearable_ts(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_wearable_timeseries(nwbfile, device)
    return nwbfile

@pytest.fixture
def write_nwb_with_wearable_timeseries(tmp_path, nwb_with_wearable_ts):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_wearable_ts)

    return tmp_path

@pytest.fixture
def nwb_with_wearable_events(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_wearable_events(nwbfile, device)
    return nwbfile


@pytest.fixture
def write_nwb_with_wearable_events(tmp_path, nwb_with_wearable_events):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_wearable_events)

    return tmp_path


def test_wearables_timeseries(write_nwb_with_wearable_timeseries):
    expected_timestamps = np.arange(0, 3600, 30)
    np.random.seed(0)
    expected_wearable_values = np.random.random(size=(120,2))

    with NWBHDF5IO(write_nwb_with_wearable_timeseries, 'r') as io:
        nwbfile = io.read()

        # ensure processing module is in the file
        assert 'wearables' in nwbfile.processing, 'Wearables processing module is missing.'
        wearables_module = nwbfile.processing["wearables"]

        # ensure wearable timeseries is in file
        assert 'test_wearable_timeseries' in wearables_module.data_interfaces, "Wearable timeseries data not present in processing module"
        # ensure data is correct
        wearable_timeseries = wearables_module.get('test_wearable_timeseries')
        # validate shape
        assert wearable_timeseries.data.shape == expected_wearable_values.shape, "Incorrect wearables timeseries data shape"
        assert wearable_timeseries.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape"
        # validate data values
        np.testing.assert_array_equal(wearable_timeseries.data[:], expected_wearable_values, "Mismatch in wearable timeseries values")
        np.testing.assert_array_equal(wearable_timeseries.timestamps[:], expected_timestamps, "Mismatch in timestamps")
        
        # validate metadata
        assert 'test_wearable_device' in nwbfile.devices, "Wearable device is missing"

        # ensure wearabletimeseries has link to wearabledevice
        assert wearable_timeseries.wearable_device is nwbfile.devices['test_wearable_device']

# Testing WearableEvents based on EventsRecord inheritance
def test_wearable_events(write_nwb_with_wearable_events):

    with NWBHDF5IO(write_nwb_with_wearable_events, 'r') as io:
        nwbfile = io.read()

        assert 'wearables' in nwbfile.processing, "Wearables processing module is missing"
        wearables = nwbfile.processing["wearables"]

        assert 'test_wearable_events' in wearables.data_interfaces.keys(), 'Missing wearable events data!'
        events = wearables.get('test_wearable_events')

        workout_event = events.get(slice(None)) # get all events
        np.testing.assert_array_equal(workout_event.timestamp[:], [10.0, 30.0, 120.0])
        assert events.wearable_device.name == "test_wearable_device"

