import pytest
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import ActivityClassSeries  # Assumes ActivityClassSeries is registered in the namespace and accessible via get_class

def add_activityclass_data(nwbfile, device):
    # Generate activity class labels
    timestamps = np.arange(0., 3600, 30)  # Every 30 seconds for 1 hour
    np.random.seed(42)
    labels = np.array(['sitting', 'walking', 'running'])
    activityclass_values = np.tile(labels, 40)[:120]

    # Create ActivityClassSeries object
    activityclass_series = ActivityClassSeries(
        name='ActivityClass Data',
        data=activityclass_values,
        unit='label',
        timestamps=timestamps,
        description='Example activity classification labels',
        wearable_device=device,
        algorithm='model_v1'  # or your actual algorithm name
    )

    # Add activity class data to the wearables processing module
    nwbfile.processing["wearables"].add_container(activityclass_series)

    return nwbfile


@pytest.fixture
def nwb_with_activityclass_data(wearables_nwbfile_device):
    nwbfile, device = wearables_nwbfile_device
    nwbfile = add_activityclass_data(nwbfile, device)
    return nwbfile


@pytest.fixture
def write_nwb_with_activityclass_data(tmp_path, nwb_with_activityclass_data):
    with NWBHDF5IO(tmp_path, 'w') as io:
        io.write(nwb_with_activityclass_data)
    return tmp_path


def test_activityclass_write_read(write_nwb_with_activityclass_data):
    '''
    Test that ActivityClassSeries can be written and read from an NWB file.
    '''
    # Expected test data
    np.random.seed(42)
    labels = np.array(['sitting', 'walking', 'running'])
    expected_activityclass_values = np.tile(labels, 40)[:120]
    expected_timestamps = np.arange(0., 3600, 30)

    # Read the NWB file
    with NWBHDF5IO(write_nwb_with_activityclass_data, 'r') as io:
        nwbfile = io.read()

        # Confirm wearables module exists
        assert 'wearables' in nwbfile.processing, 'Wearables processing module is missing.'

        # Check the ActivityClassSeries interface
        wearables = nwbfile.processing['wearables']
        assert 'ActivityClass Data' in wearables.data_interfaces, 'ActivityClassSeries is missing.'

        activityclass_series = wearables.get('ActivityClass Data')

        # Validate shape and content
        assert activityclass_series.data.shape == expected_activityclass_values.shape, "Incorrect data shape."
        assert activityclass_series.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape."
        np.testing.assert_array_equal(activityclass_series.data[:], expected_activityclass_values)
        np.testing.assert_array_equal(activityclass_series.timestamps[:], expected_timestamps)
