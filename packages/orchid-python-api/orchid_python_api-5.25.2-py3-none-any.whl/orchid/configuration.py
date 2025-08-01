#  Copyright (c) 2017-2025 KAPPA
#
#  Licensed under the Apache License, Version 2.0 (the "License"); 
#  you may not use this file except in compliance with the License. 
#  You may obtain a copy of the License at 
#
#      http://www.apache.org/licenses/LICENSE-2.0 
#
#  Unless required by applicable law or agreed to in writing, software 
#  distributed under the License is distributed on an "AS IS" BASIS, 
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
#  See the License for the specific language governing permissions and 
#  limitations under the License. 
#
# This file is part of Orchid and related technologies.
#

import glob
import logging
import os
import pathlib
from typing import Dict, Any
import warnings
import toolz.curried as toolz
import yaml

from orchid.version import get_orchid_sdk_version


_logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    pass


# Constants for environment variable names
ORCHID_ROOT_ENV_VAR = 'ORCHID_ROOT'
ORCHID_TRAINING_DATA_ENV_VAR = 'ORCHID_TRAINING_DATA'


def get_environment_configuration() -> Dict[str, Dict[str, str]]:
    """
    Gets the API configuration from the system environment.

    Returns:
        The configuration, if any, calculated from the system environment.
    """
    environment_configuration = {'orchid': {key: os.environ[env_var] for key, env_var in
                                            [('root', ORCHID_ROOT_ENV_VAR), ('training_data', ORCHID_TRAINING_DATA_ENV_VAR)] if env_var in os.environ}}
    _logger.debug(f'environment configuration = {environment_configuration}')
    return environment_configuration


def get_fallback_configuration() -> Dict[str, Dict[str, str]]:
    """
    Returns final fallback API configuration.

    Returns:
        A Python dictionary with the default (always available configuration).

    Warning:
        Although we have striven to make the default configuration a working configuration, we can only ensure
        that the default configuration meets the minimal "syntax" required by the Python API. For example, if
        Orchid is **not** installed in the default location, and the `directory` key is not overridden by a
        higher priority configuration, the Python API will **fail** to load the Orchid assemblies and throw
        an exception at runtime.
    """

    # Symbolically, the standard location for the installed Orchid binaries is
    # `$ProgramFiles/Reveal Energy Services, Inc/Orchid/<version-specific-directory>`. The following code
    # calculates an actual location by substituting the current version number for the symbol,
    # `<version-specific-directory>`.
    program_files_path = os.environ.get("ProgramFiles")
    fallback = {}
    if program_files_path is not None:
        orchid_version = get_orchid_sdk_version() + '.*'
        python_api_lib_pattern_path = os.path.join(program_files_path, 'Reveal Energy Services', 'Orchid', orchid_version, 'Orchid-'+orchid_version, 'PythonApiLibs')
        matching_paths = glob.glob(python_api_lib_pattern_path)
        if len(matching_paths) == 1:
            python_api_lib_path = matching_paths[0]
            _logger.info(f"PythonApiLibs path found : {python_api_lib_path}")
            fallback = {'orchid': {'root': str(matching_paths[0])}}
        elif len(matching_paths) == 0:
            _logger.info(f"PythonApiLibs path not found for {str(python_api_lib_pattern_path)}")
        else:
            warnings.warn(f'Fallback configuration found multiple matches for {str(python_api_lib_pattern_path)}')
        _logger.debug(f'fallback configuration={fallback}')
    return fallback


def get_file_configuration() -> Dict[str, Any]:
    """
    Returns the API configuration read from the file system.

    Returns:
        A python dictionary with the default (always available configuration).
    """

    # This code looks for the configuration file, `python_api.yaml`, in the `.orchid` sub-directory of the
    # user-specific (and system-specific) home directory. See the Python documentation of `home()` for
    # details.
    file = {}
    file_config_path = pathlib.Path.home().joinpath('.orchid', 'python_api.yaml')
    if file_config_path.exists():
        with file_config_path.open('r') as in_stream:
            file = yaml.full_load(in_stream)
    _logger.debug(f'file configuration={file}')
    return file


def get_configuration() -> Dict[str, Dict[str, Any]]:
    """
    Calculate the configuration for the Python API.

        Returns: The Python API configuration.
    """

    fallback_configuration = get_fallback_configuration()
    file_configuration = get_file_configuration()
    env_configuration = get_environment_configuration()

    configuration_dict = merge_configurations(fallback_configuration, file_configuration, env_configuration)
    if not configuration_dict.get('orchid') or (configuration_dict.get('orchid') and not configuration_dict['orchid'].get('root')):
        raise ConfigurationError("You must create an environment variable ORCHID_ROOT or a config file to set up the path to the PythonApiLibs folder since it's not in the default location")

    _logger.debug(f'result configuration={configuration_dict}')
    return configuration_dict


def merge_configurations(fallback_configuration: Dict[str, Dict[str, str]], file_configuration: Dict[str, Dict[str, Any]], env_configuration: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    # The rules for merging these configurations is not the same as a simple dictionary. The rules are:
    # - If two different configurations share a top-level key, merge the second level dictionaries.
    # - Then merge the distinct top-level keys.
    distinct_top_level_keys = set(toolz.concat([fallback_configuration.keys(),
                                                file_configuration.keys(),
                                                env_configuration.keys()]))
    result = {}
    for top_level_key in distinct_top_level_keys:
        fallback_child_configuration = fallback_configuration.get(top_level_key, {})
        file_child_configuration = file_configuration.get(top_level_key, {})
        env_child_configuration = env_configuration.get(top_level_key, {})
        child_configuration = toolz.merge(fallback_child_configuration,
                                          file_child_configuration,
                                          env_child_configuration)
        result[top_level_key] = child_configuration
    return result


def training_data_path() -> pathlib.Path:
    """
    Returns the path of the directory containing the Orchid training data.

    Returns:
        The Orchid training data path.

    Raises:
        This function raises KeyError if the training directory path is not available from the package
        configuration.
    """
    result = pathlib.Path(toolz.get_in(['orchid', 'training_data'], get_configuration()))
    return result
