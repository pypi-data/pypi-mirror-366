import pytest
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import HeartRateSeries  # Assumes HeartRateSeries is correctly implemented

def add_heart_rate_data(nwbfile, device):
    # Generate heart rate data
    timestamps = np.arange(0., 3600, 5)  # Every 5 seconds for 1 hour
    np.random.seed(42)
    heart_rate_values = np.random.randint(60, 100, size=len(timestamps))

    # Create HeartRateSeries object
    heart_rate_series = HeartRateSeries(
        name='Heart Rate Data',
        data=heart_rate_values,
        unit='bpm',
        timestamps=timestamps,
        description='Example Heart Rate data',
        wearable_device= device,
        algorithm='simulated data' # or another appropriate string
    )

    # Add heart rate data to the wearables processing module
    nwbfile.processing["wearables"].add_container(heart_rate_series)

    return nwbfile

@pytest.fixture
def nwb_with_heart_rate_data(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_heart_rate_data(nwbfile, device)
    return nwbfile

@pytest.fixture
def write_nwb_with_heart_rate_data(tmp_path, nwb_with_heart_rate_data):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_heart_rate_data)
    return tmp_path

def test_heart_rate_write_read(write_nwb_with_heart_rate_data):
    '''
    Test that HeartRateSeries can be written and read from an NWB file.
    '''
    # Regenerate the expected test data
    np.random.seed(42)
    expected_heart_rate_values = np.random.randint(60, 100, size=720)
    expected_timestamps = np.arange(0., 3600, 5)

    # Read the NWB file
    with NWBHDF5IO(write_nwb_with_heart_rate_data, 'r') as io:
        nwbfile = io.read()

        # Ensure the processing module exists
        assert 'wearables' in nwbfile.processing, 'Wearables processing module is missing.'

        # Check that HeartRateSeries is present
        wearables = nwbfile.processing['wearables']
        assert 'Heart Rate Data' in wearables.data_interfaces, 'HeartRateSeries is missing.'

        heart_rate_series = wearables.get('Heart Rate Data')

        # Validate data and timestamps
        assert heart_rate_series.data.shape == expected_heart_rate_values.shape, "Incorrect data shape."
        assert heart_rate_series.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape."

        np.testing.assert_array_equal(heart_rate_series.data[:], expected_heart_rate_values, "Mismatch in heart rate values.")
        np.testing.assert_array_equal(heart_rate_series.timestamps[:], expected_timestamps, "Mismatch in timestamps.")
