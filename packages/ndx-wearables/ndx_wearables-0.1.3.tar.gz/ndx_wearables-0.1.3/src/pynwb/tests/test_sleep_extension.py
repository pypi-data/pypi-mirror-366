import pytest
import numpy as np
from datetime import datetime
import pytz
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import ProcessingModule
from ndx_wearables import SleepStageSeries

@pytest.fixture
def nwb_with_sleep_stages(tmp_path):
    '''
    Creates a temporary NWB file with SleepStageSeries for testing.
    Returns the file path.
    '''
    nwbfile = NWBFile(
        session_description='Example sleep study session',
        identifier='TEST_SLEEP',
        session_start_time=datetime.now(pytz.timezone('America/Chicago')),
    )

    # Generate sleep stage data
    timestamps = np.arange(0., 3600, 30)  # Every 30 seconds for 1 hour
    stages = np.random.RandomState(42).choice(['awake', 'light_sleep', 'deep_sleep', 'rem'], size=len(timestamps))

    # Create SleepStageSeries object
    sleep_stage_series = SleepStageSeries(
        name='Sleep Stages',
        data=stages,
        unit='stage',
        timestamps=timestamps,
        description='Example sleep stage data'
    )

    # Add to a processing module
    sleep_module = ProcessingModule(
        name='sleep',
        description='Sleep stage data'
    )
    sleep_module.add(sleep_stage_series)
    nwbfile.add_processing_module(sleep_module)

    # Save NWB file to a temporary directory
    file_path = tmp_path / 'test_sleep.nwb'
    with NWBHDF5IO(file_path, 'w') as io:
        io.write(nwbfile)

    return file_path

@pytest.mark.skip("SleepStageSeries has not yet been updated to include WearablesBase")
def test_sleep_stage_write_read(nwb_with_sleep_stages):
    '''
    Test that SleepStageSeries can be written and read from an NWB file.
    '''
    # Regenerate the expected test data
    expected_timestamps = np.arange(0., 3600, 30)  # Every 30 seconds for 1 hour
    expected_stages = np.random.RandomState(42).choice(['awake', 'light_sleep', 'deep_sleep', 'rem'], size=len(expected_timestamps))

    # Read the NWB file
    with NWBHDF5IO(nwb_with_sleep_stages, 'r') as io:
        nwbfile = io.read()

        # Check that the processing module exists
        assert 'sleep' in nwbfile.processing, 'Sleep processing module is missing.'

        # Check that the SleepStageSeries exists
        sleep_stage_data = nwbfile.processing['sleep']
        assert 'Sleep Stages' in sleep_stage_data.data_interfaces, 'SleepStageSeries is missing.'

        sleep_series = sleep_stage_data.get('Sleep Stages')

        # Validate shape
        assert sleep_series.data.shape == expected_stages.shape, "Incorrect sleep stage data shape."
        assert sleep_series.timestamps.shape == expected_timestamps.shape, "Incorrect timestamp shape."

        # Validate actual data values (IMPORTANT)
        np.testing.assert_array_equal(sleep_series.data[:], expected_stages, "Mismatch in sleep stage values.")
        np.testing.assert_array_equal(sleep_series.timestamps[:], expected_timestamps, "Mismatch in timestamps.")

        # Validate metadata
        assert sleep_series.description == "Example sleep stage data", "Incorrect description."
