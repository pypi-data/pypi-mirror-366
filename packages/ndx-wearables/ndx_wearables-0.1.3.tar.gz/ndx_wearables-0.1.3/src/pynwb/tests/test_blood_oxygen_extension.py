import pytest
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import BloodOxygenSeries  # Assumes BloodOxygenSeries is registered in the namespace and accessible via get_class

def add_blood_oxygen_data(nwbfile, device):
    # Generate blood oxygen data
    timestamps = np.arange(0., 3600, 30)  # Every 30 seconds for 1 hour
    np.random.seed(42)
    blood_oxygen_values = np.random.randint(90, 100, size=120)  # Random SpO2 values

    # Create BloodOxygenSeries object
    blood_oxygen_series = BloodOxygenSeries(
        name='BloodOxygen Data',
        data=blood_oxygen_values,
        unit='percent',
        timestamps=timestamps,
        description='Example blood oxygen data',
        wearable_device= device,
        algorithm='pulse_oximeter'  # or another appropriate string
    )

    # Add blood oxygen data to the wearables processing module
    nwbfile.processing["wearables"].add_container(blood_oxygen_series)

    return nwbfile


@pytest.fixture
def nwb_with_blood_oxygen_data(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_blood_oxygen_data(nwbfile, device)
    return nwbfile


@pytest.fixture
def write_nwb_with_blood_oxygen_data(tmp_path, nwb_with_blood_oxygen_data):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_blood_oxygen_data)
    return tmp_path


def test_blood_oxygen_write_read(write_nwb_with_blood_oxygen_data):
    '''
    Test that BloodOxygenSeries can be written and read from an NWB file.
    '''
    # Expected test data
    np.random.seed(42)
    expected_blood_oxygen_values = np.random.randint(90, 100, size=120)
    expected_timestamps = np.arange(0., 3600, 30)

    # Read the NWB file
    with NWBHDF5IO(write_nwb_with_blood_oxygen_data, 'r') as io:
        nwbfile = io.read()

        # Confirm wearables module exists
        assert 'wearables' in nwbfile.processing, 'Wearables processing module is missing.'

        # Check the BloodOxygenSeries interface
        wearables = nwbfile.processing['wearables']
        assert 'BloodOxygen Data' in wearables.data_interfaces, 'BloodOxygenSeries is missing.'

        blood_oxygen_series = wearables.get('BloodOxygen Data')

        # Validate shape and content
        assert blood_oxygen_series.data.shape == expected_blood_oxygen_values.shape, "Incorrect data shape."
        assert blood_oxygen_series.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape."
        np.testing.assert_array_equal(blood_oxygen_series.data[:], expected_blood_oxygen_values)
        np.testing.assert_array_equal(blood_oxygen_series.timestamps[:], expected_timestamps)
