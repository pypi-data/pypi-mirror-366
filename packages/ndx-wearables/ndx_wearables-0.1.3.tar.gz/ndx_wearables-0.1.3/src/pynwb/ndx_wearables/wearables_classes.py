from pynwb import register_class, get_class, NWBContainer
from pynwb.core import MultiContainerInterface
from hdmf.common import SimpleMultiContainer
from pynwb.device import Device
from pynwb.spec import NWBGroupSpec, NWBDatasetSpec, NWBNamespaceBuilder, NWBAttributeSpec
from pynwb.base import TimeSeries, NWBDataInterface
from ndx_events import EventsTable, CategoricalVectorData
from hdmf.utils import docval, popargs, get_docval, get_data_shape
from datetime import datetime
from dateutil.tz import tzlocal
import numpy as np

# when extending NWBContainer, define __nwbfields__
# tells PyNWB properties of the NWBContainer extension
@register_class("WearableDevice", "ndx-wearables")
class WearableDevice(Device):
    '''
    - name
    - description
    - manufacturer
    - location (on body)
    '''
    __nwbfields__ = ("location",)

    @docval(
        *get_docval(Device.__init__)
        + (
            {"name":"location", "type": str, "doc": "Location on body of device"},
            {"name":"os_software_version", "type": str, "doc":"The version number of the OS/software for the WearableDevice", "default": None}
        )
    )

    def __init__(self, **kwargs):
        location = popargs("location", kwargs)
        os_software_version = popargs("os_software_version", kwargs)
        super().__init__(**kwargs)

        self.location = location
        self.os_software_version = os_software_version
  
  
class WearableBase(object):
    """
    HDMF and by extension NWB does not really support multiple inheritance.
    As a result, this class is "invisibly" inherited as a mixin

    For this to work properly, the inheriting class (at the time of writing, WearableTimeSeries and WearableEvents)
    must append the result of get_wearables_docval() to the docval of the init method, and call the function
    wearables_init_helper in the init method.
    """

    @staticmethod
    def get_wearables_docval():
        return (
            {
                'name': 'wearable_device',
                'type': 'WearableDevice',
                'doc': 'Link to the WearableDevice used to record the data'
            },
            {
                'name': 'algorithm',
                'type': str,
                'doc': 'Algorithm used to extract data from raw sensor readings'
            }
        )

    def wearables_init_helper(self, **kwargs):
        wearable_device = popargs('wearable_device', kwargs)
        algorithm = popargs('algorithm', kwargs)

        self.wearable_device = wearable_device
        self.algorithm = algorithm
        return kwargs
    
@register_class("WearableTimeSeries", "ndx-wearables")
class WearableTimeSeries(WearableBase, TimeSeries):
   # __nwbfields__ = TimeSeries.__nwbfields__ + ("algorithm",)

    @docval(
        *(get_docval(TimeSeries.__init__) + WearableBase.get_wearables_docval())
    )
    def __init__(self, **kwargs):
        kwargs = self.wearables_init_helper(**kwargs)
        super().__init__(**kwargs)

PhysiologicalMeasure = get_class("PhysiologicalMeasure", "ndx-wearables")
# @register_class('PhysiologicalMeasure', "ndx-wearables")
# class PhysiologicalMeasure(NWBDataInterface, MultiContainerInterface):
#     # TODO: this custom class registration would be nice but it throws a
#     #      TypeError: Cannot create a consistent method resolution
#     #      order (MRO) for bases NWBDataInterface, MultiContainerInterface
#
#     """
#     LFP data from one or more channels. The electrode map in each published ElectricalSeries will
#     identify which channels are providing LFP data. Filter properties should be noted in the
#     ElectricalSeries description or comments field.
#     """
#
#     __clsconf__ = [
#         {'attr': 'wearable_series',
#          'type': WearableTimeSeries,
#          'add': 'add_wearable_series',
#          'get': 'get_wearable_series',
#          'create': 'create_wearable_series'}]


# Adding events to inherit from ndx-wearables:
# WearableEvents inherits from EventsTable (from rly/ndx-events) to store timestamped discrete events from wearables
@register_class("WearableEvents", "ndx-wearables")
class WearableEvents(WearableBase, EventsTable):
   # __nwbfields__ = ("algorithm",)

    @docval(
        *(get_docval(EventsTable.__init__) + WearableBase.get_wearables_docval())
    )
    def __init__(self, **kwargs):
        kwargs = self.wearables_init_helper(**kwargs)
        super().__init__(**kwargs)

