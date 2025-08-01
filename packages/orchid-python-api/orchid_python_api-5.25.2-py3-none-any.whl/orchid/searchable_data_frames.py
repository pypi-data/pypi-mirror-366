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

import warnings
from typing import Callable, Iterator

import toolz.curried as toolz

from orchid import searchable_project_objects as spo

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics import IProjectObject


class SearchableDataFrames(spo.SearchableProjectObjects):
    def __init__(self, make_adapter: Callable, net_project_objects: Iterator[IProjectObject]):
        super(SearchableDataFrames, self).__init__(make_adapter, net_project_objects)

        def has_duplicate_object_ids(pos):
            return not toolz.pipe(
                pos,
                toolz.map(lambda npo: npo.ObjectId.ToString()),
                toolz.isdistinct,
            )

        if has_duplicate_object_ids(net_project_objects):
            warnings.warn("""
            KNOWN ISSUE: Multiple data frames with duplicate object IDs detected.
            
            Workarounds:
            - **DO NOT** use `find_by_object_id`; use `find_by_name` or `find_by_display_name` to search.
            - Delete and recreate all data frames in a release of Orchid > 2022.3.
            """)
