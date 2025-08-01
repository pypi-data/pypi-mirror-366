# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.FractureDiagnostics.FiberDataSet import IFiberDataSet
import orchid.base
from orchid import (
    dom_project_object as dpo,
    native_fiber_data_set_info as info
)
from .utils import convert_dotnet_datetime_to_python_datetime
from typing import List, Optional
from datetime import datetime
import pandas as pd

INT32_MAX = 2147483647


class NativeFiberData(dpo.DomProjectObject):
    """Adapts a native IFiberDataSet to python."""

    def __init__(self, net_fiber_data_set: IFiberDataSet):
        """
        Constructs an instance adapting a .NET IFiberDataSet.
        Args:
            net_fiber_data_set: The .NET fiber data set to be adapted.
        """
        super().__init__(net_fiber_data_set, orchid.base.constantly(net_fiber_data_set.Project))

    @property
    def file_path(self) -> str:
        return self.dom_object.FilePath

    @property
    def depth_unit(self) -> str:
        return self.dom_object.DepthUnit

    @property
    def timezone_info(self) -> str:
        return self.dom_object.TimeZoneInfo

    @property
    def times_data_set(self) -> str:
        return self.dom_object.TimesDataSet

    @property
    def data_sets_info(self) -> List[info.NativeFiberDataSetInfo]:
        return [info.NativeFiberDataSetInfo(x) for x in self.dom_object.FiberDataSets]

    def get_data_set(self, data_set_name: Optional[str] = None):
        try:
            data_set_info = next(x for x in self.dom_object.FiberDataSets if x.name == data_set_name) if data_set_name is not None else self.dom_object.FiberDataSets[0]
        except StopIteration:
            raise ValueError("No Data Set with this name in this fiber data object")
        data = self.dom_object.GetDataSet(data_set_info)
        data_list = [[data[i, j] for j in range(data.GetLength(1))] for i in range(data.GetLength(0))]
        return pd.DataFrame(data_list)

    def get_data_table(self, start_index: int = 0, end_index: int = INT32_MAX):
        if end_index == INT32_MAX:
            print("We strongly recommend that you avoid loading the entire data table and instead work with chunks, "
                  "specifying the start and end indexes. You can also use the get_data_set method, which is faster.")
        print("Retrieving the data table... This may take a few minutes")
        data_table = self.dom_object.GetDataTable(self.dom_object.DepthUnit, start_index, end_index)
        data_dict = {column: [row[column] for row in data_table.Rows] for column in data_table.Columns}
        df = pd.DataFrame(data_dict)
        print("Data table Retrieved")
        return df

    @property
    def dates(self) -> List[datetime]:
        return [convert_dotnet_datetime_to_python_datetime(x.ToString()) for x in self.dom_object.Times]

    @property
    def depths(self) -> List[float]:
        return [x.Value for x in self.dom_object.Depths]
