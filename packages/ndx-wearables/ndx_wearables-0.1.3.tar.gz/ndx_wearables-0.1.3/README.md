# ndx-wearables Extension for NWB

Store data from wearable devices in NWB

This extension is designed to help store data collected from a wide variety of wearable devices in a cross-device 
capable way, and with an eye towards clinical applications.
For more details about the extension, see the paper "NDX-Wearables: An NWB Extension for Clinical Neuroscience" 
(submitted to NER 2025).


## Installation

Create a new Python environment. Python 3.11 works well, python 3.8-3.12 have been tested.

```terminal
conda create -n <env_name> python=3.11
```
You should be able to install from pypi using `pip install ndx-wearables`

If you would like to install and contribute to developing the package, follow the instructions below 
in [Installing in editable mode](#Installing-in-editable-mode)

## Usage

To see how the data stored using this extension looks, visit our example dataset on the
[EMBER Archive](https://dandi.emberarchive.org/dandiset/000207).

You can also generate a local copy of a synthetic dataset by running the `examples/all_modalities.py` script.


## Notes on Extension Usage

Several of the modality-specific extensions (e.g., `BloodOxygenSeries`, `HeartRateSeries`, etc.) now require additional
arguments beyond the usual `name`, `data`, and `timestamps`.

In particular:
- `wearable_device` is required for classes that link to a device (e.g., `BloodOxygenSeries`, `VO2MaxSeries`)
- `algorithm` is required for many classes to indicate how the data was derived (e.g., `HRVSeries`, `StepCountSeries`)

If these arguments are omitted, instantiating the class will raise an error. You can find working examples in the test 
scripts under `src/pynwb/tests`.

## Arguments for ndx-wearables Classes

#### TimeSeries (WearableTimeSeries) based modalities

| Class Name             | Required Arguments                                                     | Optional Arguments                            |
|------------------------|------------------------------------------------------------------------|-----------------------------------------------|
| `ActivitySeries`       | `name`, `data`, `timestamps`, `wearable_device`, `algorithm`           | `comments`, `resolution`, `conversion`        |
| `BloodOxygenSeries`    | `name`, `data`, `timestamps`, `wearable_device`, `unit`, `algorithm`   | `resolution`, `conversion`, `comments`        |
| `HeartRateSeries`      | `name`, `data`, `timestamps`, `wearable_device`, `unit`, `algorithm`   | `resolution`, `conversion`, `comments`        |
| `HRVSeries`            | `name`, `data`, `timestamps`, `wearable_device`, `algorithm`, `sampling_rate` | `comments`, `description`, `resolution` |
| `METSeries`            | `name`, `data`, `timestamps`, `wearable_device`, `unit`, `algorithm`   | `comments`, `resolution`, `conversion`        |
| `SleepMovementSeries`  | `name`, `data`, `timestamps`, `wearable_device`, `algorithm`           | `comments`, `resolution`, `conversion`        |
| `SleepPhaseSeries`     | `name`, `data`, `timestamps`, `wearable_device`, `enums`, `algorithm`  | `resolution`, `conversion`, `comments`        |
| `StepCountSeries`      | `name`, `data`, `timestamps`, `wearable_device`, `algorithm`           | `resolution`, `conversion`, `comments`        |
| `VO2MaxSeries`         | `name`, `data`, `timestamps`, `wearable_device`, `unit`, `algorithm`   | `comments`, `resolution`, `conversion`        |


#### EventTable (WearableEvents) based modalities (WIP)

| Class Name    | Required Arguments                                                     | Optional Arguments                            |
|---------------|------------------------------------------------------------------------|-----------------------------------------------|
| `Workouts`    | `name`, `data`, `timestamps`, `wearable_device`, `algorithm`           | `comments`, `resolution`, `conversion`        |
| `SleepEvents` | `name`, `data`, `timestamps`, `wearable_device`, `unit`, `algorithm`   | `resolution`, `conversion`, `comments`        |


These reflect typical usage in constructors. For full context or updates, refer to the class definitions in
[`src/pynwb/ndx_wearables`](src/pynwb/ndx_wearables) and usage examples in [`src/pynwb/tests`](src/pynwb/tests).


## Developing the extension

We use a gitflow model for collaborative development. Each feature should be created on a branch that branches off of 
the `develop` branch. Draft PRs back into develop should be open for each WIP feature, and marked as ready for review 
once the feature is complete. Periodic releases will be made from develop into `main`.

### Installing in editable mode
Navigate to the project root `cd path/to/ndx-wearables`, then install the required dependencies. For developers, use:

```terminal
pip install -r requirements-dev.txt
```
Custom extensions are added to the extension spec YAML file by running:

```terminal
python src/spec/create_extension_spec.py
```

After running this script, you can verify that the extensions are correctly added to `spec/ndx-wearables.extensions.yaml`.

Running test code may be done with PyTest using the test files located in `src/pynwb/tests`.

To use custom extensions outside a PyTest setting, they must be registered by navigating to the directory root and installing the package:
```terminal
cd path/to/ndx-wearables
pip install -e .
```

---
This extension was created using [ndx-template](https://github.com/nwb-extensions/ndx-template).
