## Orchid Python API Release Notes

### A Reading Suggestion

This document is one of several documents you may want to read:

- [README](./README.md) - The project README file.
- [README-dev.md](./README-dev.md) - A similar file targeting for package developers.
- [ReleaseNotes.md](./ReleaseNotes.md) - The release notes for this project.

Although one can read this document in any text editor since it is simply a text file, consider installing
the [Python grip utility](https://pypi.org/project/grip/). This application allows one to "render local readme
files before sending off to GitHub". Although you need not send any of these file to `GitHub`, by using `grip` 
to render the file, you can much more easily navigate the document links.

### Release notes for 5.25.2

This release is the production release of the Orchid Python API corresponding to Orchid 5.25.2. We have made the necessary
updates to the Python API to remain compatible with the .NET API.

A minor change has been made where we've split the dependencies between the example files and the sdk dependencies for a smaller footprint when installing the API. There are probably
many ways to do this, but when installing the new package, if you want to install the example dependencies you can run `pip install .[examples]` or if using poetry `poetry install -E examples`

#### Possible breaking .NET API changes

- None

#### Resolved Issues

- None

#### Features

- None

#### Known Issues

- None

### Release notes for 5.25.1

This release is the production release of the Orchid Python API corresponding to Orchid 5.25.1. We have made the necessary
updates to the Python API to remain compatible with the .NET API.

Additionally, we have added a simple high level API to access fiber data. See `fiber_data_example.py` in the `examples\` folder.
Note that even with a small fiber data set, converting the fiber data into a `pandas` data frame takes quite
a while. Getting the data in .NET objects is fairly quick, so there may be room for other ideas there.

#### Possible breaking .NET API changes

- None

#### Resolved Issues

- None

#### Features

- None

#### Known Issues

- None

### Release notes for 5.24.4

This release is the production release of the Orchid Python API corresponding to Orchid 5.24.3. We have made the necessary
updates to the Python API to remain compatible with the .NET API.

We have also updated dependencies on the Python side. Note that we skipped the 5.24.2 release as it was a smaller, quicker release.

#### Possible breaking .NET API changes

- None

#### Resolved Issues

- None

#### Features

- None

#### Known Issues

- None

### Release notes for 5.24.3

This release is the production release of the Orchid Python API corresponding to Orchid 5.24.3. We have made the necessary
updates to the Python API to remain compatible with the .NET API.

We have also updated dependencies on the Python side. Note that we skipped the 5.24.2 release as it was a smaller, quicker release.

#### Possible breaking .NET API changes

- None

#### Resolved Issues

- None

#### Features

- None

#### Known Issues

- None

### Release notes for 5.24.1

This release is the production release of the Orchid Python API corresponding to Orchid 5.24.1. We have made the necessary
updates to the Python API to remain compatible with the .NET API.

On the .NET side, we renamed IMonitor to ITimeSeriesMonitor. The necessary updates have been made on the Python API side.
Additionally, the Shmin property was moved from IWell to IStage. As such, some tests have been updated to accommodate that change.

#### Possible breaking .NET API changes

- None

#### Resolved Issues

- None

#### Features

- None

#### Known Issues

- None

### Release notes for 5.24.0

This release is the production release of the Orchid Python API corresponding to Orchid 5.24.0. We have made the necessary
updates to the Python API to remain compatible with the .NET API.

In addition, we have updated the project to be netcore (semantically, in practice it is just called .NET) compatible. .NET Core is Microsoft's cross platform library.  Everything should behave
the same way as before, as pythonnet fully supports netcore (albeit with a few workarounds which have been implemented in this release),
but you may need to install .NET if it's not done already. As a user of Orchid, you should have these libraries pre-installed, but,
if not, you can find .NET 8 here (https://dotnet.microsoft.com/en-us/download). The latest version of .NET 6 (6.0.26) should be
fine, but we recommend moving to .NET 8 if possible.

#### Possible breaking .NET API changes

- None

#### Resolved Issues

- None

#### Features

- None

#### Known Issues

- None

### Release notes for 5.23.322

This release is the production release of the Orchid Python API corresponding to Orchid 5.23.322. We have made the necessary
updates to the Python API to remain compatible with the .NET API.

#### Possible breaking .NET API changes

- None

#### Resolved Issues

- None

#### Features

- None

#### Known Issues

- None



### Release notes for 5.22.299

This release is the production release of the Orchid Python API corresponding to Orchid 5.22.299.

#### Possible breaking .NET API changes

- None

#### Resolved Issues

- None

#### Features

- None

#### Known Issues

- None


### Release notes for 2023.1.220

This release is the production release of the Orchid Python API corresponding to Orchid 2023.1.220. A very basic example of how
to get to a project's well horizon markers was added. Additionally, a fix to an integration test is included.

#### Possible breaking .NET API changes

- None

#### Resolved Issues

- None

#### Features

- None

#### Known Issues

- None

### Release notes for 2022.4.252

This release is the production release of the Orchid Python API corresponding to Orchid 2022.4.252. The main
features in this release are the upgrade of the internal package, `pythonnet`, to version `3.x`, and the change 
requiring Python 3.10 for the runtime environment.

#### Possible breaking .NET API changes

- The Orchid Python API no longer uses `pythonnet-2.x`; instead, it requires at least `pythonnet-3.0.0.post1`.
- The Orchid Python API no longer supports Python 3.8; instead it requires at least Python 3.10.
- Orchid now requires specifying a time zone when reading a project from disk. A typical default value for this argument
  is `System.TimeZoneInfo.Utc` but this value should specify the time actual time zone of the project itself.

#### Resolved Issues

- None

#### Features

- Upgrade dependencies of the Orchid Python API to `pythonnet-3.x`. This upgrade causes some examples to break. See the
  two files below for examples of breakages discovered by the development team.
  - [Breakages because of Python.NET 3](./README-pythonnet3.md)
  - [Breakages in low-level code because of Python.NET 3](./README-pythonnet3-low.md)
- Upgrade the minimum Python version from 3.8 to 3.10. This upgrade is needed to support the upgrade to `pythonnet-3.x`.

#### Known Issues

- The upgrade to `pythonnet-3.x` causes some code and examples to break. See the two files below for examples of 
  breakages discovered by the development team.
  - [Breakages because of Python.NET 3](./README-pythonnet3.md)
  - [Breakages in low-level code because of Python.NET 3](./README-pythonnet3-low.md)
- One must change the minimum Python version from 3.8 to 3.10 (required by `pythonnet-3.x`).

### Release notes for 2022.3.273

This release is the production release of the Orchid Python API corresponding to Orchid 2022.3.273. The main 
feature in this release is support for data frames with columns containing the .NET type `System.Guid`. (A "GUID" is a
globally unique identifier. Orchid uses GUIDs internally to identify domain objects such as wells, stages, and data
frames.) Additionally, this release contains a small number of minor changes to keep the API, its examples, and 
its documentation consistent with Orchid.

#### Possible breaking .NET API changes

- None

#### Resolved Issues

- [GitHub issue 38](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/38)

#### Features

- Data frames
  - Implements support for reading data frames with columns of the .NET type, `System.Guid`
  - Provides a warning if the Orchid Python API detects data frames with **duplicated** object IDs. This issue 
    is a known issue with Orchid releases at or below 2022.3. In addition to calling attention to the issue, the 
    Python warning documents workarounds for this issue.

#### Known Issues

- None

### Release notes for 2022.2.338

This release is the production release of the Orchid Python API corresponding to Orchid 2022.2.338. This release has
neither additional features nor bug fixes but uses a default installation of Orchid 2022.2.338 with no
additional configuration.

#### Possible breaking .NET API changes

- None

#### Resolved Issues

- None

#### Features

- None

#### Known Issues

- None

### Release notes for 2022.2.324

This release is the production release of the Orchid Python API corresponding to Orchid 2022.2. This release:

- Implements a high-level (Pythonic) API to create stages and add them to a well
- Improves performance when loading an Orchid project by using a new .NET feature to load projects in parallel
- Implements a high-level "fast save" API. This API provides an optimized way of saving Orchid projects when
  certain conditions are met.
- Restore minimum Python version to 3.8.3
- Repaired `pandas.DataFrame.append` "Future Warning" in examples
- Add low-level example demonstrating creating and adding multi-picking observations to an observation set

#### Possible breaking .NET API changes

- .NET API renames `StageCorrectionStatus` to `CorrectionStatus`
- Added comments describing a work-around for the integer-valued stage attribute limitation
- Change the implementation of the Python API for stages to handle optional .NET values for the stage properties,
  `Isip`, `PNet` and `Shmin`
- When installing 2022.2.324 in an orchid environment using Python 3.8.3 that has spyder installed using `conda`, 
  `conda` reports the following error:

  >>> ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
  >>> spyder-kernels 2.1.3 requires jupyter-client<7,>=5.3.4, but you have jupyter-client 7.3.4 which is incompatible.
  >>> pylint 2.9.6 requires astroid<2.7,>=2.6.5, but you have astroid 2.12.2 which is incompatible. 

#### Resolved Issues

- [GitHub issue 35](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/35)
- [GitHub issue 34](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/34)
- [GitHub issue 33](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/33)
- [GitHub issue 32](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/32)

#### Features

- Well and Stage
  - Implements a high-level (Pythonic) API to create stages and add them to a well
  - Adds an example illustrating use of this API
  - Renames the original low-level example to `add_stages_low.py` to better communicate intent

- Saving projects
  - Implements an optimized but possibly unsafe function to save Orchid projects. If certain conditions are met
    (described in the docstring for `orchid.core.optimized_but_possibly_unsafe_save()`), one can use this function to
    save Orchid projects. The developer must determine if the particular use case meets the conditions to safely save
    the project using the optimized but possibly unsafe function.
    
    If the use case does not meet the conditions, the function, `orchid.core.save_project()`, safely saves the
    complete project, but, most likely, takes additional time over the optimized but possibly unsafe save function.

- Examples (high-level)
  - Add tutorial script to create stages and add them to a well

- Examples (low-level)
  - Repaired low-level (Python.NET) script to create stages and add them to a well
  - Add a low-level script demonstrating adding multi-picking observations to an observation set.

- Distribution
  - Reduce minimum required Python version to 3.8.3.

#### Known Issues

- [GitHub issue 36](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/36)
- [GitHub issue 37](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/37)

### Release notes for 2022.1.360

This release is the production release of the Orchid Python API corresponding to Orchid 2022.1. This release:

- Provides high-level access to downhole proppant concentrations
- Adds a high-level API property to change the stage time range
- Add a high-level example script to illustrate using the high-level API to change the stage time range
- Expose stage QC results via the high-level API
- Replace low-level script to read and write stage QC results with script invoking the high-level API
  (`stage_qc_results.py`)
- Repaired the low-level example script to create stage attributes to reflect changes to the .NET API
  (`auto_pick_and_create_stage_attribute.py`)
- Clarify documentation of the `PythonApiLibs` directory in configuration documentation

#### Resolved Issues

- [GitHub issue 25](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/25)
- [GitHub issue 26](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/26)
- [GitHub issue 28](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/28)
- [GitHub issue 30](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/30)
- [GitHub issue 31](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/31)

#### Features

- Project
  - Expose `user_data` property containing stage QC results

- Stage
  - Change the stage start and stop times (time range)

- Treatment curves
  - Add enumeration `DOWNHOLE_PROPPANT_CONCENTRATION` to access this data from the API

- Project user data
  - Create class `NativeUserDataAdapter` to provide read and write access to this information

- Examples (high-level)
  - Add script to read and write stage QC results
  - Add script to change the stage start and stop times
  - 
- Examples (low-level)
  - Repaired script to create stage attributes
  - Removed script to query the stage QC results using the low-level API

- Distribution
  - None

#### Known Issues

- [GitHub issue 27](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/27)
- [GitHub issue 29](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/29)

### Release notes for 2021.4.283

This release is the production release of the Orchid Python API corresponding to Orchid 2021.4. This release:

- Adds several low-level examples
- Repairs stage center MDKB calculation
- Adds well trajectory methods
- Clarifies installed package requirements
- Work-around to clarify `PythonApiLibs` in configuration

#### Resolved Issues

- [GitHub issue 24](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/24)

#### Features

- Well trajectory
  - TVDSS
  - Inclination
  - Azimuth
  - MDKB

- Project
  - Clarifies direction of project azimuth

- Stage
  - Corrects stage center MDKB calculation

- Examples (low-level)
  - Adding observations and saving changed projects
  - Matching low-level monitor time series and high-level project time series (A low-level workaround for
    [GitHub issue 17](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/17)
  - Creating stage attributes
    
- Distribution
  - Adds generation of `requirements.txt` to release process

#### Known Issues

- [GitHub issue 25](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/25)

### Release notes for 2021.3.406

This release is a hot fix release of the Orchid Python API corresponding to the hot fix for Orchid 2021.3. 
This release:

- Improves the performance of the `plot_time_series` example
- Improves the performance of the `volume_2_first_response` example

#### Resolved Issues

- [GitHub issue 23](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/23)

#### Features

No additional features as part of this release.

#### Known Issues

No additional know issues for this release.

### Release notes for 2021.3.381

This release is the production release of the Orchid Python API corresponding to Orchid 2021.3. This release:

- Adds an iterator over "searchable project objects"
- Add a tutorial demonstrating how to navigate the project
- Prototype developer scripts to generate documentation using Sphinx

#### Resolved Issues

- [GitHub issue 22](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/22)

#### Features

- SearchableProjectObjects
  - Make class an iterator

- Tutorials
  - A notebook and script demonstrating project object navigation

#### Known Issues

No additional know issues for this release.

### Release notes for 2021.2.316

This release is the production release of the Orchid Python API corresponding to Orchid 2021.2. This release:

- Updates to the latest version of `numpy`
- Exposes data frames via the API
- Internally uses `pendulum` for improved handling of date times (both UTC and local times)
- Provides a consistent interface for collections of DOM objects

#### Resolved Issues

- [GitHub issue 12](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/12)
- [GitHub issue 16](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/16)
- [GitHub issue 18](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/18)
- [GitHub issue 21](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/21)

#### Features

- Project
  - Data frames
- Stage
  - Find stages by:
    - Display stage number
    - Display name with well

- Object collections
  - Find object(s) by
    - Display name
    - Name
    - Object ID
    - All objects satisfying a predicate (primarily a convenience for use cases where the condition of interest does 
      not involve identifying information). Note that stages have some of these convenience methods already.
  - Query collection for
    - All display names
    - All names
    - All object IDs
    - All objects (primarily a convenience for use cases where one wants all objects in the collection independent 
      of identifying information)

- Examples
  - Scripts for each example notebook
  - A notebook and script demonstrating search and data frame access.

#### Known Issues

- [GitHub issue 19](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/19)

### Release notes for 2021.1.399

This release is the second production release of the Orchid Python API. This release changes the 
implementation of measurements to use the [pint](https://pint.readthedocs.io/en/stable/) package and adds
access to additional Orchid features.

#### Resolved issues

- [GitHub issue 6](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/6)
- [GitHub issue 10](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/10)
- [GitHub issue 13](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/13)
- [GitHub issue 14](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/14)
- [GitHub issue 15](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/15)

#### Features

- Project
  - Azimuth
  - Fluid density
  - Project bounds
  - Project center (and center location)
  - Monitors
- Well
  - Formation
  - Wellhead location
- Monitor
  - Name
  - Display name
  - Start time
  - Stop time
  - Time range (contains start and stop time)
- Examples
  - Volume to first response
  
Replace custom `Measurement` class with the features available in `pint`.

#### Known issues

- [GitHub issue 18](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/18)
  
  This issue is a deprecation warning from `matplotlib`. It began occurring after updating the package
  dependencies. We do not believe this error will affect customer code.

- [GitHub issue 16](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/16)
  
  All monitor curves can be access indirectly via the `Project.monitor_curves()` method. The work-around for
  this issue is then to search for curves by with a matching name.
  
- [GitHub issue 17](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/17)

  The work-around is to search the iterable returned by Project.monitor_curves for a curve with the name of
  the monitor of interest. Because of issue #16, beware that this work around may not return all monitors
  with the name of interest.

### Release notes for 2020.4.690

This release is the first production release of the Orchid Python API. This release offers access to the
following Orchid features.

#### Features

- General
  - Loading Orchid `.ifrac` files
- Project
  - Name
  - Project units
  - Wells
  - Default well colors
  - Monitor curves
  - Searching for wells by name
- Well
  - Name
  - Display name
  - Stages
  - Trajectory
  - UWI
- Stage
  - Cluster count
  - Display name with well
  - Display name without well
  - Display stage number
  - Global stage sequence number
  - Order of completion on well
  - Stage (formation connection) type
  - Start time
  - Stop time
  - Bottom location
  - Center location
    - In addition, to the subsurface point
      - Easting
      - Northing
      - Measured depth (MD)
      - Total vertical depth (TVD) relative to
        - Ground level
        - Seal level
      - XY (both easting and northing)
  - Cluster location
  - Instantaneous shut in pressure (ISIP)
  - Measured depth of stage top
  - Measured depth of stage bottom
  - Net pressure (PNet)
  - Minimum shear (ShMin)
  - Stage length
  - Top location
  - Treatment curves
- TimeSeries (monitor and treatment curves)
  - Name
  - Display name
  - Sampled quantity name
  - Sampled quantity unit
  - Time series
- Calculations
  - For treatment
    - Median treating pressure
    - Pumped fluid volume
    - Total proppant mass

#### Known issues

- [GitHub issue 18](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/18)
  
  This issue is a deprecation warning from `matplotlib`. It began occurring after updating the package
  dependencies. We do not believe this error will affect customer code.
  
- [GitHub issue 14](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/14)

  The work-around for this issue is to configure the locations of both Orchid training data and the Orchid
  binaries.

- [GitHub issue 13](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/13)

  We believe that this warning is caused by the `pandas` package interacting with `numpy`, and plan to
  investigate this issue.

- [GitHub issue 12](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/12)
  
  Some versions of `numpy` encounter an issue with the `fmod` function on Windows. The current work-around
  fixes the version of `numpy` at 1.19.3.
  
- [GitHub issue 10](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/10)

  Although we have increased the scope of our internal testing to cover many more units of measure, we plan to
  implement the convenience function suggested by the author.
  
- [GitHub issue 6](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/6)

  This issue is an internal issues and currently has no effect on installation or usage of the API.

- [GitHub issue 3](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/3)

  This issue may relate to `numpy` 1.19.1 (the version mentioned in the issue). We plan to retest against 
  `numpy` 1.19.3. We have had no other reports of this issue.
