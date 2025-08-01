"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.
    Defines user- and privilege-related structures returned by the
    Insight 5 REST API.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from typing import List, Literal

from .config import InsightApiBaseModel
from .references import Reference


class User(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-User-Admin.html?scroll=_components_schemas_User """
    apps: List[Reference] = []
    authority_groups: List[Reference] = []
    email: str = ''
    first_name: str = ''
    id: str
    last_name: str = ''
    name: str = ''
    object_type: Literal['USER'] = 'USER'
    status: str
    username: str
