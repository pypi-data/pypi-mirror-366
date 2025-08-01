# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.FractureDiagnostics.FiberDataSet import IFiberDataSetInfo
import orchid.base
from orchid import (
    dot_net_dom_access as dna,
    dom_project_object as dpo,
    dot_net_disposable as dnd,
    net_date_time as ndt,
)
import json


class NativeFiberDataSetInfo(dpo.DomProjectObject):
    """Adapts a native IFiberDataSet to python."""

    def __init__(self, net_fiber_data_set_info: IFiberDataSetInfo):
        """
        Constructs an instance adapting a .NET IFiberDataSet.
        Args:
            net_fiber_data_set_info: The .NET fiber data set to be adapted.
        """
        super().__init__(net_fiber_data_set_info)

    description = dna.dom_property('description', 'Description')
    type = dna.dom_property('type', 'Type')
    unit = dna.dom_property('unit', 'Unit of this data set')
    min = dna.dom_property('min', 'Minimum value of this data set')
    max = dna.dom_property('max', 'Maximum value of this data set')
