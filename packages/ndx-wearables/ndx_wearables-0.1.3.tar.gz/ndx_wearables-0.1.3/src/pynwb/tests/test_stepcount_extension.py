import pytest
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import StepCountSeries  # Assumes StepCountSeries is registered in the namespace and accessible via get_class

def add_stepcount_data(nwbfile, device):
    # Generate step count data
    timestamps = np.arange(0., 3600, 30)  # Every 30 seconds for 1 hour
    np.random.seed(42)
    stepcount_values = np.random.randint(0, 200, size=120)  # Random step count values

    # Create StepCountSeries object
    stepcount_series = StepCountSeries(
        name='StepCount Data',
        data=stepcount_values,
        unit='steps',
        timestamps=timestamps,
        description='Example step count values',
        wearable_device= device,
        algorithm='test_algorithm', # or another appropriate string
    )

    # Add step count data to the wearables processing module
    nwbfile.processing["wearables"].add_container(stepcount_series)

    return nwbfile


@pytest.fixture
def nwb_with_stepcount_data(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_stepcount_data(nwbfile, device)
    return nwbfile


@pytest.fixture
def write_nwb_with_stepcount_data(tmp_path, nwb_with_stepcount_data):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_stepcount_data)
    return tmp_path


def test_stepcount_write_read(write_nwb_with_stepcount_data):
    '''
    Test that StepCountSeries can be written and read from an NWB file.
    '''
    # Expected test data
    np.random.seed(42)
    expected_stepcount_values = np.random.randint(0, 200, size=120)
    expected_timestamps = np.arange(0., 3600, 30)

    # Read the NWB file
    with NWBHDF5IO(write_nwb_with_stepcount_data, 'r') as io:
        nwbfile = io.read()

        # Confirm wearables module exists
        assert 'wearables' in nwbfile.processing, 'Wearables processing module is missing.'

        # Check the StepCountSeries interface
        wearables = nwbfile.processing['wearables']
        assert 'StepCount Data' in wearables.data_interfaces, 'StepCountSeries is missing.'

        stepcount_series = wearables.get('StepCount Data')

        # Validate shape and content
        assert stepcount_series.data.shape == expected_stepcount_values.shape, "Incorrect data shape."
        assert stepcount_series.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape."
        np.testing.assert_array_equal(stepcount_series.data[:], expected_stepcount_values)
        np.testing.assert_array_equal(stepcount_series.timestamps[:], expected_timestamps)
