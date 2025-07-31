import pytest
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import SleepPhaseSeries  # Assumes SleepPhaseSeries is registered in the namespace and accessible via get_class

def add_sleepphase_data(nwbfile, device):
    # Generate sleep phase labels
    timestamps = np.arange(0., 3600, 30)  # Every 30 seconds for 1 hour
    np.random.seed(42)
    labels = np.array(['REM', 'Light', 'Deep'])
    sleepphase_values = np.tile(labels, 40)[:120]

    # Create SleepPhaseSeries object
    sleepphase_series = SleepPhaseSeries(
        name='SleepPhase Data',
        data=sleepphase_values,
        unit='label',
        timestamps=timestamps,
        description='Example sleep phase labels',
        wearable_device= device,
        algorithm='test_algorithm', # or another appropriate string
    )

    # Add sleep phase data to the wearables processing module
    nwbfile.processing["wearables"].add_container(sleepphase_series)

    return nwbfile


@pytest.fixture
def nwb_with_sleepphase_data(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_sleepphase_data(nwbfile, device)
    return nwbfile


@pytest.fixture
def write_nwb_with_sleepphase_data(tmp_path, nwb_with_sleepphase_data):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_sleepphase_data)
    return tmp_path


def test_sleepphase_write_read(write_nwb_with_sleepphase_data):
    '''
    Test that SleepPhaseSeries can be written and read from an NWB file.
    '''
    # Expected test data
    np.random.seed(42)
    labels = np.array(['REM', 'Light', 'Deep'])
    expected_sleepphase_values = np.tile(labels, 40)[:120]
    expected_timestamps = np.arange(0., 3600, 30)

    # Read the NWB file
    with NWBHDF5IO(write_nwb_with_sleepphase_data, 'r') as io:
        nwbfile = io.read()

        # Confirm wearables module exists
        assert 'wearables' in nwbfile.processing, 'Wearables processing module is missing.'

        # Check the SleepPhaseSeries interface
        wearables = nwbfile.processing['wearables']
        assert 'SleepPhase Data' in wearables.data_interfaces, 'SleepPhaseSeries is missing.'

        sleepphase_series = wearables.get('SleepPhase Data')

        # Validate shape and content
        assert sleepphase_series.data.shape == expected_sleepphase_values.shape, "Incorrect data shape."
        assert sleepphase_series.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape."
        np.testing.assert_array_equal(sleepphase_series.data[:], expected_sleepphase_values)
        np.testing.assert_array_equal(sleepphase_series.timestamps[:], expected_timestamps)
