import pytest
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import VO2maxSeries #Assuming VO2maxSeries is correctly implemented in ndx_wearables/yaml file

def add_vo2max_data(nwbfile, device):
    # Generate VO2 max data
    timestamps = np.arange(0., 3600, 30)  # Every 30 seconds for 1 hour
    np.random.seed(42)
    vo2_max_values = np.random.randint(30, 60, size=120)  # Random VO2 max values in mL/kg/min

    # Create VO2MaxSeries object
    vo2max_series = VO2maxSeries(
        name='VO2 Max Data',
        data=vo2_max_values,
        unit='mL/kg/min',  # VO2 max units
        timestamps=timestamps,
        description='Example VO2 max data',
        wearable_device=device,
        algorithm='test_algorithm',
    )

    # add heart rate data to the wearables processing module
    nwbfile.processing["wearables"].add_container(vo2max_series)

    return nwbfile

@pytest.fixture
def nwb_with_vo2max_data(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_vo2max_data(nwbfile, device)
    return nwbfile

@pytest.fixture
def write_nwb_with_vo2max_data(tmp_path, nwb_with_vo2max_data):

    # Save NWB file
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_vo2max_data)

    return tmp_path

def test_vo2max_write_read(write_nwb_with_vo2max_data):
    '''
    Test that VO2MaxSeries can be written and read from an NWB file.
    '''
    # Regenerate the expected test data with the correct timestamps
    np.random.seed(42)  # Ensure reproducibility
    expected_vo2_max_values = np.random.randint(30, 60, size=120)
    expected_timestamps = np.arange(0., 3600, 30)  # Correct to match the 30-second interval

    # Read the NWB file
    with NWBHDF5IO(write_nwb_with_vo2max_data, 'r') as io:
        nwbfile = io.read()

        # Ensure the fitness data processing module is present
        assert 'wearables' in nwbfile.processing, 'Fitness data processing module is missing.'

        # Ensure the VO2MaxSeries data interface is present
        wearables = nwbfile.processing['wearables']
        assert 'VO2 Max Data' in wearables.data_interfaces, 'VO2MaxSeries is missing.'

        vo2max_series = wearables.get('VO2 Max Data')

        # Validate the shape of the data
        assert vo2max_series.data.shape == expected_vo2_max_values.shape, "Incorrect VO2 max data shape."
        assert vo2max_series.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape."

        # Validate the data values
        np.testing.assert_array_equal(vo2max_series.data[:], expected_vo2_max_values, "Mismatch in VO2 max values.")
        np.testing.assert_array_equal(vo2max_series.timestamps[:], expected_timestamps, "Mismatch in timestamps.")