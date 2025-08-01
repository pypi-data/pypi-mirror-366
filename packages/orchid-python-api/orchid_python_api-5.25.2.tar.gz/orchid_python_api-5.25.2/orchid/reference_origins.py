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

import enum

# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.FractureDiagnostics import WellReferenceFrameXy as NetWellReferenceFrameXy
# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.FractureDiagnostics import DepthDatum as NetDepthDatum


# TODO: Consider adding base with methods like `toNetEnum` and `fromNetEnum`
class WellReferenceFrameXy(enum.Enum):
    ABSOLUTE_STATE_PLANE = NetWellReferenceFrameXy.AbsoluteStatePlane
    PROJECT = NetWellReferenceFrameXy.Project
    WELL_HEAD = NetWellReferenceFrameXy.WellHead


# TODO: Consider adding base with methods like `toNetEnum` and `fromNetEnum`
class DepthDatum(enum.Enum):
    GROUND_LEVEL = NetDepthDatum.GroundLevel
    KELLY_BUSHING = NetDepthDatum.KellyBushing
    SEA_LEVEL = NetDepthDatum.SeaLevel
