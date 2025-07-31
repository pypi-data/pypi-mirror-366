import pytest
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import SleepMovementSeries  # Assumes SleepMovementSeries is registered in the namespace and accessible via get_class

def add_sleepmovement_data(nwbfile, device):
    # Generate sleep movement data
    timestamps = np.arange(0., 3600, 30)  # Every 30 seconds for 1 hour
    np.random.seed(42)
    sleepmovement_values = np.random.rand(120)  # Random float values [0, 1)

    # Create SleepMovementSeries object
    sleepmovement_series = SleepMovementSeries(
        name='SleepMovement Data',
        data=sleepmovement_values,
        unit='a.u.',  # Arbitrary units
        timestamps=timestamps,
        description='Example sleep movement values',
        wearable_device= device,
        algorithm='test_algorithm', # or another appropriate string
    )

    # Add sleep movement data to the wearables processing module
    nwbfile.processing["wearables"].add_container(sleepmovement_series)

    return nwbfile


@pytest.fixture
def nwb_with_sleepmovement_data(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_sleepmovement_data(nwbfile, device)
    return nwbfile


@pytest.fixture
def write_nwb_with_sleepmovement_data(tmp_path, nwb_with_sleepmovement_data):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_sleepmovement_data)
    return tmp_path


def test_sleepmovement_write_read(write_nwb_with_sleepmovement_data):
    '''
    Test that SleepMovementSeries can be written and read from an NWB file.
    '''
    # Expected test data
    np.random.seed(42)
    expected_sleepmovement_values = np.random.rand(120)
    expected_timestamps = np.arange(0., 3600, 30)

    # Read the NWB file
    with NWBHDF5IO(write_nwb_with_sleepmovement_data, 'r') as io:
        nwbfile = io.read()

        # Confirm wearables module exists
        assert 'wearables' in nwbfile.processing, 'Wearables processing module is missing.'

        # Check the SleepMovementSeries interface
        wearables = nwbfile.processing['wearables']
        assert 'SleepMovement Data' in wearables.data_interfaces, 'SleepMovementSeries is missing.'

        sleepmovement_series = wearables.get('SleepMovement Data')

        # Validate shape and content
        assert sleepmovement_series.data.shape == expected_sleepmovement_values.shape, "Incorrect data shape."
        assert sleepmovement_series.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape."
        np.testing.assert_array_equal(sleepmovement_series.data[:], expected_sleepmovement_values)
        np.testing.assert_array_equal(sleepmovement_series.timestamps[:], expected_timestamps)
