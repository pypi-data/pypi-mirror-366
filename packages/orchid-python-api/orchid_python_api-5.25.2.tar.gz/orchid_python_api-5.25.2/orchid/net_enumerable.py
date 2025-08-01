#
# This file is part of Orchid and related technologies.
#
# Copyright (c) 2017-2025 KAPPA.  All Rights Reserved.
#
# LEGAL NOTICE:
# Orchid contains trade secrets and otherwise confidential information
# owned by KAPPA. Access to and use of this information is
# strictly limited and controlled by the Company. This file may not be copied,
# distributed, or otherwise disclosed outside of the Company's facilities 
# except under appropriate precautions to maintain the confidentiality hereof, 
# and may not be used in any way not expressly authorized by the Company.
#

"""Defines conversions involving .NET IEnumerable instances."""

from functools import singledispatch
from typing import List

# noinspection PyUnresolvedReferences
import orchid  # Only to call `pythonnet.load('netfx')`

from pythonnet import load
load('coreclr')

# noinspection PyUnresolvedReferences,PyPackageRequirements
import clr
# noinspection PyUnresolvedReferences
clr.AddReference('System.Collections')
# noinspection PyUnresolvedReferences
clr.AddReference('DynamicData')

# noinspection PyUnresolvedReferences,PyPackageRequirements
from System.Collections import IEnumerable
# noinspection PyUnresolvedReferences,PyPackageRequirements
from DynamicData import (IObservableCache, IObservableList)


@singledispatch
def as_list(net_object) -> List:
    raise NotImplementedError


@as_list.register(IEnumerable)
def as_list_from_enumerable(net_object) -> List:
    """
    Convert a .NET `IEnumerable` to a Python `list`.

    Args:
        net_object: An .NET instance implementing the `IEnumerable` (and `IEnumerable<T>`) interfaces.

    Returns:
        The Python `list` containing the same items as the source .NET `IEnumerable`.

    """
    return [i for i in net_object]


@as_list.register(IObservableCache)
@as_list.register(IObservableList)
def as_list_from_dynamic_data(net_object) -> List:
    """
    Convert a .NET `IEnumerable` to a Python `list`.

    Args:
        net_object: An .NET instance implementing the `IEnumerable` (and `IEnumerable<T>`) interfaces.

    Returns:
        The Python `list` containing the same items as the source .NET `IEnumerable`.

    """
    return [i for i in net_object.Items]
