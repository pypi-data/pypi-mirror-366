import pytest
from pathlib import Path
from tests import make_wearables_nwbfile, add_wearables_device

@pytest.fixture(scope='session')
def tmp_path():
    return Path('./src/pynwb/tests/test_nwb_file.nwb')

@pytest.fixture(scope='session')
def wearables_nwbfile():
    nwbfile = make_wearables_nwbfile()
    return nwbfile

@pytest.fixture(scope='session')
def wearables_nwbfile_device(wearables_nwbfile):
    nwbfile = wearables_nwbfile
    nwbfile, device = add_wearables_device(nwbfile)
    return nwbfile, device