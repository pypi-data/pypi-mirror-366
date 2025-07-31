import os
from pynwb import load_namespaces, get_class, available_namespaces

try:
    from importlib.resources import files
except ImportError:
    # TODO: Remove when python 3.9 becomes the new minimum
    from importlib_resources import files

print(f'Initial namespaces: {available_namespaces()}')

# Load the spec for NDX-Events first
import ndx_events
__events_spec = ndx_events.__spec_path
events_ns = load_namespaces(str(__events_spec))

print(f'After events: {available_namespaces()}')

# Get path to the namespace.yaml file with the expected location when installed not in editable mode
__location_of_this_file = files(__name__)
__spec_path = __location_of_this_file / "spec" / "ndx-wearables.namespace.yaml"

# If that path does not exist, we are likely running in editable mode. Use the local path instead
if not os.path.exists(__spec_path):
    __spec_path = __location_of_this_file.parent.parent.parent / "spec" / "ndx-wearables.namespace.yaml"

# Load the namespace
load_namespaces(str(__spec_path))

# TODO: Define your classes here to make them accessible at the package level.
# Safe fallback if the namespace was not found in original logic
import pathlib
if not os.path.exists(__spec_path):
    print("Namespace not found in the default paths, trying fallback...")
    
    # Get the location of this file
    fallback_path = pathlib.Path(__file__).parent / "ndx-wearables.namespace.yaml"

    # Try to load from the fallback path
    if os.path.exists(fallback_path):
        print(f"Namespace found in fallback path: {fallback_path}")
        load_namespaces(str(fallback_path))
    else:
        print(f"Namespace not found in fallback path: {fallback_path}")

# Import the base classes
from .wearables_classes import *

# Generate classes for individual modalities on the fly
EnumTimeSeries = get_class("EnumTimeSeries", "ndx-wearables")
SleepStageSeries = get_class("SleepStageSeries", "ndx-wearables")
HRVSeries = get_class("HRVSeries", "ndx-wearables")
VO2maxSeries = get_class("VO2maxSeries", "ndx-wearables")
HeartRateSeries = get_class("HeartRateSeries", "ndx-wearables")
BloodOxygenSeries = get_class("BloodOxygenSeries", "ndx-wearables")
StepCountSeries = get_class("StepCountSeries", "ndx-wearables")
MetSeries = get_class("MetSeries", "ndx-wearables")
SleepMovementSeries = get_class("SleepMovementSeries", "ndx-wearables")
ActivityClassSeries = get_class("ActivityClassSeries", "ndx-wearables")
SleepPhaseSeries = get_class("SleepPhaseSeries", "ndx-wearables")

print(f'Final: {available_namespaces()}')

# Remove these functions from the package
del load_namespaces, get_class
