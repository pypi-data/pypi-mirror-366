import pytest
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import MetSeries  # Assumes MetSeries is registered in the namespace and accessible via get_class

def add_met_data(nwbfile, device):
    # Generate MET data
    timestamps = np.arange(0., 3600, 30)  # Every 30 seconds for 1 hour
    np.random.seed(42)
    met_values = np.random.uniform(1.0, 10.0, size=120)  # Random MET values

    # Create MetSeries object
    met_series = MetSeries(
        name='Met Data',
        data=met_values,
        unit='MET',
        timestamps=timestamps,
        description='Example metabolic equivalent values',
        wearable_device= device,
        algorithm='test_algorithm', # or another appropriate string
    )

    # Add MET data to the wearables processing module
    nwbfile.processing["wearables"].add_container(met_series)

    return nwbfile


@pytest.fixture
def nwb_with_met_data(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_met_data(nwbfile, device)
    return nwbfile


@pytest.fixture
def write_nwb_with_met_data(tmp_path, nwb_with_met_data):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_met_data)
    return tmp_path


def test_met_write_read(write_nwb_with_met_data):
    '''
    Test that MetSeries can be written and read from an NWB file.
    '''
    # Expected test data
    np.random.seed(42)
    expected_met_values = np.random.uniform(1.0, 10.0, size=120)
    expected_timestamps = np.arange(0., 3600, 30)

    # Read the NWB file
    with NWBHDF5IO(write_nwb_with_met_data, 'r') as io:
        nwbfile = io.read()

        # Confirm wearables module exists
        assert 'wearables' in nwbfile.processing, 'Wearables processing module is missing.'

        # Check the MetSeries interface
        wearables = nwbfile.processing['wearables']
        assert 'Met Data' in wearables.data_interfaces, 'MetSeries is missing.'

        met_series = wearables.get('Met Data')

        # Validate shape and content
        assert met_series.data.shape == expected_met_values.shape, "Incorrect data shape."
        assert met_series.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape."
        np.testing.assert_array_equal(met_series.data[:], expected_met_values)
        np.testing.assert_array_equal(met_series.timestamps[:], expected_timestamps)
