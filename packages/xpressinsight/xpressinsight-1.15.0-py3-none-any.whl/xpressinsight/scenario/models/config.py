"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.
    Defines standard configuration for serializing models

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""

from pydantic import ConfigDict, BaseModel
from pydantic.alias_generators import to_camel


class InsightApiBaseModel(BaseModel):
    """ Base class defining a common config for the JSON models used by Insight v5 REST API """
    model_config = ConfigDict(
        #
        alias_generator=to_camel,
        #
        populate_by_name=True,
        #
        extra='ignore',
        #
        defer_build=True,
        #
        #
        #
        #
        #
        protected_namespaces=()
    )
