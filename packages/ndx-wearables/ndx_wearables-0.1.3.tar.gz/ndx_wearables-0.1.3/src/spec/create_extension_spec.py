# -*- coding: utf-8 -*-
import os.path
from pynwb.spec import NWBNamespaceBuilder, export_spec, NWBGroupSpec, NWBAttributeSpec
from wearables_infrastructure import make_wearables_infrastructure
# TODO: import other spec classes as needed
# from pynwb.spec import NWBDatasetSpec, NWBLinkSpec, NWBDtypeSpec, NWBRefSpec
import sleep
import hrv
import vo2max
import heart_rate
import blood_oxygen
import step_count
import met
import sleep_movement
import activity_class
import sleep_phase


def main():
    # these arguments were auto-generated from your cookiecutter inputs
    ns_builder = NWBNamespaceBuilder(
        name="""ndx-wearables""",
        version="""0.1.1""",
        doc="""Store data from human wearable devices in NWB""",
        author=[
            "Tomasz M. Fraczek",
            "Lauren Diaz",
            "Nicole Guittari",
            "Rick Hanish",
            "Timon Merk",
            "Nicole Tregoning",
            "Sandy Hider",
            "Wayne K. Goodman",
            "Sameer A. Sheth",
            "Han Yi",
            "Brock A. Wester",
            "Jeffery A. Herron",
            "Erik C. Johnson",
            "Nicole R. Provenza"
        ],
        contact=[
            "tomek.fraczek@bcm.edu", 
        ],
    )
    ns_builder.include_namespace("core")
    ns_builder.include_namespace("ndx-events")

    wearables_infra_datastructures = make_wearables_infrastructure()
    sleep_stage_series = sleep.make_sleep_stage()
    hrv_series = hrv.make_hrv_stage()
    vo2max_series = vo2max.make_vo2max_stage()
    heart_rate_series = heart_rate.make_heart_rate_stage()
    blood_oxygen_series = blood_oxygen.make_blood_oxygen_stage()
    step_count_series = step_count.make_step_count_stage()
    met_series = met.make_met_stage()
    sleep_movement_series = sleep_movement.make_sleep_movement_stage()
    activity_class_series = activity_class.make_activity_class_stage()
    sleep_phase_series = sleep_phase.make_sleep_phase_stage()

# TODO: add all of your new data types to this list

    # Combine all series types
    new_data_types = [
        *wearables_infra_datastructures,
        hrv_series,
        vo2max_series,
        sleep_stage_series,
        heart_rate_series,
        blood_oxygen_series,
        step_count_series,
        met_series,
        sleep_movement_series,
        activity_class_series,
        sleep_phase_series
    ]


    # export the spec to yaml files in the spec folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "spec"))
    export_spec(ns_builder, new_data_types, output_dir)


if __name__ == "__main__":
    # usage: python create_extension_spec.py
    main()
