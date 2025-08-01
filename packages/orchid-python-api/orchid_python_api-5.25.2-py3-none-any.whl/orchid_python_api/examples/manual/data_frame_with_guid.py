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

# ** WARNING **
#
# This example is only temporary.

import uuid

import orchid


def open_data_frame():
    orchid_training_data_path = orchid.training_data_path()
    print('Wait for project to load...')
    project = orchid.load_project(str(orchid_training_data_path.joinpath('05PermianProjectQ3_2022_DataFrames.ifrac')))
    project_data_frame = project.data_frames().find_by_object_id(uuid.UUID('cd97a60c-6e74-404d-90f0-d04b54968267'))
    to_display = ('No such data frame' if project_data_frame is None else project_data_frame.pandas_data_frame())
    print()
    print(to_display)


if __name__ == '__main__':
    print('** WARNING **')
    print('This example is only temporary.')
    print()

    open_data_frame()
