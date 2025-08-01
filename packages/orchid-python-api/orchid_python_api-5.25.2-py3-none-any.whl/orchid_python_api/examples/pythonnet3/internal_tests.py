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

"""
Script demonstrating the changes to repair the internal tests after upgrading Python.NET 3.
"""


# Repairs of Python.NET 3 breaking changes to internal tests

# 0 Load a runtime before calling `import clr`

# In order to access .NET assemblies (`.dll` files), one must load an available runtime before executing the
# `import clr` statement. (If one calls `import clr` before specifying a runtime, Python.NET will load a default
# runtime which may **not** be compatible with the installed Orchid assemblies.
#
# To make this easier, when we `import` the `orchid` package, the Orchid Python API will load the runtime
# corresponding to the configured Orchid installation.

# noinspection PyUnresolvedReferences
import orchid
from orchid import (
    net_fracture_diagnostics_factory as net_factory,
)

from pythonnet import load
load('coreclr')

# noinspection PyUnresolvedReferences,PyPackageRequirements
import clr

import pprint  # Used to "pretty-print" complex data, for example, lists
import textwrap  # Help to format pretty printed text

import pendulum

# noinspection PyUnresolvedReferences,PyPackageRequirements
from System import (
    ArgumentException,
    Convert,
    DateTime,
    DateTimeKind,
    DateTimeOffset,
    Int32,
    InvalidCastException,
    TimeSpan,
)

object_factory = net_factory.create()

DEFAULT_TEXTWRAP_WIDTH = 70


def print_underline(text, ch):
    print(textwrap.fill(text))
    print(min(len(text), DEFAULT_TEXTWRAP_WIDTH) * ch)
    print()


def title(text):
    print(min(len(text), DEFAULT_TEXTWRAP_WIDTH) * '#')
    print_underline(text, '#')


def section(text):
    print_underline(text, '=')


def sub_section(text):
    print_underline(text, '-')


def sub_sub_section(text):
    print_underline(text, '^')


def paragraph(text):
    print(textwrap.fill(text, replace_whitespace=True))
    print()


def quote(text):
    print(textwrap.fill(text, replace_whitespace=True, initial_indent='> ', subsequent_indent='> '))
    print()


# noinspection DuplicatedCode
def banner(banner_text):
    print(len(banner_text) * '=')
    print(banner_text)
    print(len(banner_text) * '=')
    print()


def empty_line():
    print()


def pretty_print_with_header(item, header, max_lines=None):
    header_text = f'`{header}` returns:'
    pretty_printed_text = (textwrap
                           .TextWrapper(initial_indent=2 * ' ', subsequent_indent=(2 + 1) * ' ', max_lines=max_lines)
                           .fill(f'{pprint.pformat(item)}'))
    text_to_print = f'{header_text}\n{pretty_printed_text}'
    print(text_to_print)
    print()


def pretty_print_net_item_with_header(net_item, header, max_lines=None):
    header_text = f'`{header}.ToString()` returns:'
    pretty_printed_text = (textwrap
                           .TextWrapper(initial_indent=2 * ' ', subsequent_indent=(2 + 1) * ' ', max_lines=max_lines)
                           .fill(f'{pprint.pformat(net_item.ToString())}'))
    text_to_print = f'{header_text}\n{pretty_printed_text}'
    print(text_to_print)
    print()


def pretty_print_with_error(error_callable, error_type, header, max_lines=None):
    header_text = f'Trying {header} raises:'
    try:
        error_callable()
    except error_type as et:
        pretty_printed_text = (textwrap
                               .TextWrapper(initial_indent=2 * ' ', subsequent_indent=(2 + 1) * ' ',
                                            max_lines=max_lines)
                               .fill(f'{pprint.pformat(et)}'))
        text_to_print = f'{header_text}\n{pretty_printed_text}'
        print(text_to_print)
    print()


def wait_for_input():
    input('Press enter to continue...')
    print()


section('1 Reduce the implicit conversions between Python types and .NET Types')

sub_section('1.1 Equality between Python `int` values and `DateTimeOffset.MaxValue` no longer supported')

paragraph("""Under Python.NET 2.5.2, one could test for equality between .NET `Enum` members and Python `int` 
values.""")

paragraph("""Under Python.NET 3, this test raises a `TypeError`.""")

try:
    108 == DateTimeOffset.MaxValue
except TypeError as te:
    print(f'TypeError: {te}')

try:
    108 == TimeSpan.MaxValue
except TypeError as te:
    print(f'TypeError: {te}')
empty_line()

# We filed an issue with the Python.NET team. They responded with the following:

# > Yes, we tried to limit the implicit" conversions to a minimum. I don't even know which
# > change in particular is responsible for the behavioural ~change~ fix that you are observing here, but you are only
# > able to compare things to a .NET object that are directly convertible to it. If you'd really require this for
# > `DateTimeOffset` and TimeSpan`, you could make them convertible via a
# > [Codec](https://pythonnet.github.io/pythonnet/codecs.html). Otherwise, I'd suggest you just generate the respective
# > comparison values using `.FromTicks`.

paragraph("""Under Python.NET 3, one must explicitly use the `Ticks` property in the equality test.""")
108 == DateTimeOffset.MaxValue.Ticks
108 == TimeSpan.MaxValue.Ticks
108 == TimeSpan.MinValue.Ticks

wait_for_input()

sub_section('1.2 Less effort to make Python constructors "just work"')

paragraph("""Under Python.NET 2.5.2, expressions like `TimeSpan()` just worked. (Note that the .NET `TimeSpan` class 
**does not** have a default constructor.)""")

paragraph("""Under Python.NET 3, executing `TimeSpan()` raises a `TypeError`.""")
try:
    TimeSpan()
except TypeError as te:
    print(f'TypeError: {te}')
empty_line()

paragraph("""Under Python.NET 3, one must explicitly supply an argument to the `TimeSpan` constructor (perhaps zero 
(0)), or one must use methods like `TimeSpan.FromTicks()""")

TimeSpan(8801)
TimeSpan(0)
TimeSpan.FromTicks(0)

wait_for_input()

section('2 Adding attributes with integer values requires conversion')

# (This issue occurred in **both** internal testing and low-level script testing and so is duplicated.)

paragraph("""Under Python.NET 2.5.2, one could supply a Python `int` value to the `SetAttribute` call for an 
`IAttribute` with a `System.Int32` value.""")

paragraph('(This scenario requires significant set up. Please wait patiently...)')

# Find the well named 'Demo_1H'
bakken = orchid.load_project('c:/src/Orchid.IntegrationTestData/frankNstein_Bakken_UTM13_FEET.ifrac')
candidate_wells = list(bakken.wells().find_by_name('Demo_1H'))
assert len(candidate_wells) == 1
demo_1h = candidate_wells[0]

# Create an attribute with name, 'My New Attribute', and type, `System.Int32`
attribute_to_add_type = Int32
attribute_to_add = object_factory.CreateAttribute[attribute_to_add_type]('My New Attribute', -1)

# Add newly created attribute to well, 'Demo_1H'
with orchid.dot_net_disposable.disposable(demo_1h.dom_object.ToMutable()) as mutable_well:
    mutable_well.AddStageAttribute(attribute_to_add)

# Find stage number 7 in well, 'Demo_1H'
maybe_stage = demo_1h.stages().find_by_display_stage_number(7)
assert maybe_stage is not None
stage_7 = maybe_stage

paragraph("""Executing this same code, under Python.NET 3, raises an `ArgumentException`.""")

# Add attribute with value, 17, to stage 7, with Python `int` type.
with (orchid.dot_net_disposable.disposable(stage_7.dom_object.ToMutable())) as mutable_stage:
    # This action will fail because the attribute type is `System.Int32`
    # and `pythonnet-3.0.0.post1` **does not** implicitly equate these two types.
    try:
        mutable_stage.SetAttribute(attribute_to_add, int)
    except ArgumentException as ae:
        print(f'ArgumentException: {ae}')
empty_line()

paragraph("""Using Python.NET 3, one must **explicitly** convert the supplied `int` to `Int32`.""")

# Add attribute to stage 7 with a value of 17 **explicitly** converted to an `Int32`
with (orchid.dot_net_disposable.disposable(stage_7.dom_object.ToMutable())) as mutable_stage:
    mutable_stage.SetAttribute(attribute_to_add, attribute_to_add_type(7))

# Verify added attribute value
ignored_object = object()
is_attribute_present, actual_attribute_value = stage_7.dom_object.TryGetAttributeValue(attribute_to_add,
                                                                                       ignored_object)
assert is_attribute_present
assert type(actual_attribute_value) == int
assert actual_attribute_value == 7

wait_for_input()

section( '3 Disabled implicit conversion from C# Enums to Python `int` and back' )

sub_section('3.1 Reduced need for and changed behavior of `Overloads` (`__overloads__` in Python.NET 3)')

# The .NET `DateTime` class has many overloaded constructors. Because version Python.NET 2.5.2 converted
# members of .NET Enum types into Python `int` values, the method resolution process could not distinguish between the
# `DateTime` constructor taking 7 `System.Int32` arguments (the last specifying milliseconds) and the constructor
# accepting 6 `System.Int32` values and a `DateTimeKind` member. Consequently, a developer of the Orchid Python API had
# to specify an overload in order to invoke the appropriate constructor.

paragraph("""Under Python 2.5.2, one used the `Overloads` attribute to select a specific overload. Additionally, the
`Overloads` attribute could be queried to return a `list` of available overloads.

Under Python 3, querying the `__overloads__` (preferred but `Overloads` is also available) produces an unexpected 
result.""")

pretty_print_with_header((DateTime.__overloads__, DateTime.Overloads), '`DateTime.__overloads__, DateTime.Overloads`')

paragraph("""Our working hypothesis is that, because the Python.NET method resolution algorithm could find any 
overloads for the constructor, executing this code under Python.NET 3 produces this behavior.""")

paragraph("""Additionally, we created an issue with the Python.NET team. In the response to our issue, the Python.NET 
team indicated that `__overloads__` was not an attribute but a [property]( https://realpython.com/python-property/).""")

pretty_print_with_header(type(DateTime.__overloads__), 'type(DateTime.__overloads__)')

wait_for_input()

sub_section('3.2 .NET Enum members are no longer converted to Python `int` values')

paragraph("""Python.NET 2.5.2 implicitly converted .NET `Enum` members to Python `int` values. Python.NET 3 exposes 
the (derived) .NET `Enum` type to Python.""")

pretty_print_with_header(type(DateTimeKind.Utc), 'type(DateTimeKind.Utc)')
pretty_print_with_header(dir(DateTimeKind.Utc), 'dir(DateTimeKind.Utc)', max_lines=5)
pretty_print_with_header(DateTimeKind.Utc.GetType(), 'DateTimeKind.Utc.GetType()')
pretty_print_with_header(dir(DateTimeKind.Utc.GetType()), 'dir(DateTimeKind.Utc.GetType())', max_lines=5)
pretty_print_with_header(DateTimeKind.Utc.GetType().BaseType, 'DateTimeKind.Utc.GetType().BaseType')
pretty_print_with_header(DateTimeKind.Utc.GetType().BaseType.FullName, 'DateTimeKind.Utc.GetType().BaseType.FullName')

paragraph("""Because Python.NET 3 retains the .NET `Enum` member, Python.NET can then resolve the `DateTime` 
7-argument constructor with the `DateTimeKind` last argument without "help".""")

pretty_print_with_header(DateTime(2021, 12, 1, 12, 15, 37, DateTimeKind.Utc).ToString('o'),
                         'DateTime(2021, 12, 1, 12, 15, 37, DateTimeKind.Utc).ToString("o")')

wait_for_input()

sub_section('3.3 Eliminated need to inherit from Python `enum.IntEnum` for compatibility with .NET Enum types')

paragraph("""Version 2.5.2 of `pythonnet` converted values of type .NET Enum to Python `int` values. Consequently, 
to support easy comparisons between the .NET type, `Orchid.FractureDiagnostics.FormationConnectionType` and the Python
enumeration, `native_stage_adapter.ConnectionType`, we defined `native_stage_adapter.ConnectionType` to inherit from 
`enum.IntEnum`.  This base class is not needed in `pythonnet-3.0.0.post1` because the enumeration member 
`native_stage_adapter.ConnectionType.PLUG_AND_PERF`, defined to have a value of 
`Orchid.FractureDiagnostics.FormationConnectionType` is no longer of type `int` but is actually of type, 
`Orchid.FractureDiagnostics.FormationConnectionType`.""")

paragraph("""Under Python.NET 2.5.2, the following expression returned `True`, but under Python.NET 3,""")
pretty_print_with_header(orchid.net_date_time.TimePointTimeZoneKind.UTC == 0,
                         'orchid.net_date_time.TimePointTimeZoneKind.UTC == 0')

paragraph("""Under Python.NET 2.5.2, the following expression also returned `True`, but under Python.NET 3""")
pretty_print_with_header(orchid.native_stage_adapter.ConnectionType == 0,
                         'orchid.native_stage_adapter.ConnectionType == 0')

paragraph("""Python.NET 3 exposes .NET `Enum` members as .NET `Enum` members instead of Python `int` values.""")

orchid.native_stage_adapter.FormationConnectionType

paragraph("""To support equality between .NET `Enum` members and the corresponding Python `enumeration` members, 
one must use the `value` property of the Python `enumeration` member.""")
orchid.native_stage_adapter.ConnectionType.PLUG_AND_PERF.value

wait_for_input()

section('4 Return values from .NET methods that return an interface are now automatically wrapped in that interface')

print("""Under `pythonnet-2.5.2`, running the following `doctest` passes:

```
>>> start = pendulum.parse('2022-02-23T15:53:23Z')
>>> stop = pendulum.parse('2022-02-24T05:54:11Z')
>>> net_start = ndt.as_net_date_time(start)
>>> net_stop = ndt.as_net_date_time(stop)
>>> factory = create()
>>> date_time_offset_range = factory.CreateDateTimeOffsetRange(net_start, net_stop)
>>> (date_time_offset_range.Start.ToString('o'), date_time_offset_range.Stop.ToString('o'))
('2022-02-23T15:53:23.0000000+00:00', '2022-02-24T05:54:11.0000000+00:00')
```
""")

wait_for_input()

print("""When running the same `doctest` using `pythonnet-3.0.0.post1`, this code
encounters an unhandled exception:

```
Error
**********************************************************************
File "C:\src\orchid-python-api\orchid\net_fracture_diagnostics_factory.py", line ?, in net_fracture_diagnostics_factory.create
Failed example:
(date_time_offset_range.Start.ToString('o'), date_time_offset_range.Stop.ToString('o'))
Exception raised:
Traceback (most recent call last):
File "C:/Users/larry.jones/AppData/Local/JetBrains/Toolbox/apps/PyCharm-P/ch-0/222.4459.20/plugins/python/helpers/pycharm/docrunner.py", line 138, in __run
exec(compile(example.source, filename, "single",
File "<doctest net_fracture_diagnostics_factory.create[6]>", line 1, in <module>
(date_time_offset_range.Start.ToString('o'), date_time_offset_range.Stop.ToString('o'))
TypeError: No method matches given arguments for Object.ToString: (<class 'str'>)
```
""")

wait_for_input()

start = pendulum.parse('2022-02-23T15:53:23Z')
stop = pendulum.parse('2022-02-24T05:54:11Z')
net_start = orchid.net_date_time.as_net_date_time(start)
net_stop = orchid.net_date_time.as_net_date_time(stop)
factory = orchid.net_fracture_diagnostics_factory.create()

paragraph("""Under Python.NET 2.5.2, the type returned by the method,
`IFractureDiagnosticsFactory.CreateDateTimeOffsetRange`, is the type of the Orchid object, `DateTimeOffsetRange`.""")

date_time_offset_range = factory.CreateDateTimeOffsetRange(net_start, net_stop)

paragraph("""Under Python.NET 3, the returned type is an **interface**.""")
pretty_print_with_header(type(date_time_offset_range), 'type(date_time_offset_range)')

paragraph("""The interface does not explicitly define `IDateTimeOffsetRange.Start` (and `Stop`) to return a 
`DateTimeOffset`; instead, these methods return instances of `IComparable`.""")
pretty_print_with_header(type(date_time_offset_range.Start), 'type(date_time_offset_range.Start)')

paragraph("""Even though the **actual** class of the returned object is a `DateTimeOffset` instance""")
pretty_print_with_header(date_time_offset_range.Start.GetType().FullName,
                         'date_time_offset_range.Start.GetType().FullName')

wait_for_input()

net_range_start = date_time_offset_range.Start
paragraph("""Invoking the method `.ToString("o")` (the overload taking a `string` argument is only supported by 
`DateTimeOffset` and **not** the `IComparable` interface) on the interface raises a `TypeError`""")
try:
    net_range_start.ToString('o')
except TypeError as te:
    print(f'TypeError: {te}')
empty_line()

paragraph("""But invoking `Object.ToString()`, which takes **no** argument, succeeds""")
net_range_start.ToString()

paragraph("""Unfortunately, no .NET conversion supports changing from the interface to the actual class""")
try:
    error_net_range_start = Convert.ChangeType(date_time_offset_range, DateTimeOffset)
    type(error_net_range_start)
except InvalidCastException as ice:
    print(f'InvalidCastException {ice}')
empty_line()

paragraph("""Although I could work around the issue by calling `ToString()`, I was not very satisfied.""")

paragraph("""After posting an [issue](https://github.com/pythonnet/pythonnet/issues/2034), I received a 
[response](https://github.com/pythonnet/pythonnet/issues/2034#issuecomment-1332728831) that stated:""")

quote("""You can access `__implementation__` (codecs applied) or `__raw_implementation__` (codecs not applied).""")

paragraph( 'This solution is a much better solution than my work around.' )

pretty_print_with_header(net_range_start.__implementation__, 'net_range_start.__implementation__')
pretty_print_with_header(net_range_start.__raw_implementation__, 'net_range_start.__raw_implementation__')
pretty_print_with_header(net_range_start.__raw_implementation__.ToString('o'),
                         'net_range_start.__raw_implementation__.ToString("o"')

wait_for_input()
