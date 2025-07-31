import pytest
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import HRVSeries #Assuming HRVSeries is correctly implemented in ndx_wearables/yaml file

def add_hrv_data(nwbfile, device):
    # Generate heart rate data
    timestamps = np.arange(0., 3600, 30)  # Every 30 seconds for 1 hour
    np.random.seed(42)
    heart_rate_values = np.random.randint(60, 100, size=120)  # Random BPM values


    # Create HRVSeries object
    hrv_series = HRVSeries(
        name='HRV Data',
        data=heart_rate_values,
        unit='bpm',  # Beats per minute
        timestamps=timestamps,
        description='Example HRV data',
        wearable_device=device,
        algorithm='test_algorithm', # or another appropriate string
    )

    # add heart rate data to the wearables processing module
    nwbfile.processing["wearables"].add_container(hrv_series)

    return nwbfile


@pytest.fixture
def nwb_with_hrv_data(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_hrv_data(nwbfile, device)
    return nwbfile


@pytest.fixture
def write_nwb_with_hrv_data(tmp_path, nwb_with_hrv_data):
    # Save NWB file
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_hrv_data)
    return tmp_path


def test_hrv_write_read(write_nwb_with_hrv_data):
    '''
    Test that HRVSeries can be written and read from an NWB file.
    '''
    # Regenerate the expected test data with the correct timestamps
    np.random.seed(42)  # Ensure reproducibility
    expected_heart_rate_values = np.random.randint(60, 100, size=120)
    expected_timestamps = np.arange(0., 3600, 30)  # Correct to match the 30-second interval

    # Read the NWB file
    with NWBHDF5IO(write_nwb_with_hrv_data, 'r') as io:
        nwbfile = io.read()

        # Ensure the cardiac health processing module is present
        assert 'wearables' in nwbfile.processing, 'Wearables processing module is missing.'

        # Ensure the HRVSeries data interface is present
        cardiac_data = nwbfile.processing['wearables']
        assert 'HRV Data' in cardiac_data.data_interfaces, 'HRVSeries is missing.'

        hrv_series = cardiac_data.get('HRV Data')

        # Validate the shape of the data
        assert hrv_series.data.shape == expected_heart_rate_values.shape, "Incorrect HRV data shape."
        assert hrv_series.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape."

        # Validate the data values
        np.testing.assert_array_equal(hrv_series.data[:], expected_heart_rate_values, "Mismatch in HRV values.")
        np.testing.assert_array_equal(hrv_series.timestamps[:], expected_timestamps, "Mismatch in timestamps.")