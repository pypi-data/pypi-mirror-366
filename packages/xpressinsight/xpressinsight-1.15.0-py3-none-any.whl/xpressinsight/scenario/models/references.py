"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.
    Defines reference-related structures returned by the Insight 5 REST API.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from typing import Optional

from .config import InsightApiBaseModel


class Reference(InsightApiBaseModel):
    """
    Declares a generic Reference model type, which can be used in place of ReferenceApp, ReferenceScenario,
    ReferenceAuthorityGroup and so forth.
    """
    #
    #
    id: str
    #
    object_type: str
    name: Optional[str] = None
