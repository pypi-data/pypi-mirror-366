"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.
    Defines portation-related structures returned by the Insight 5 REST API.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from typing import Optional, Literal, List

from .config import InsightApiBaseModel
from .references import Reference


class UpgradeRequest(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Portations.html?scroll=_components_schemas_UpgradeRequest """
    reference: Reference
    upgrade_type: str
    validate_model_name: bool


class Upgrade(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Portations.html?scroll=_components_schemas_Upgrade """
    id: str
    object_type: Literal['UPGRADE'] = 'UPGRADE'
    dismissed: bool = False
    error_messages: List[str] = None
    filename: Optional[str] = None
    finished: Optional[str] = None
    info_messages: List[str] = []
    name: Optional[str] = None
    owner: Optional[Reference] = None
    parent: Optional[Reference] = None
    started: Optional[str] = None
    status: Optional[str] = None
    validate_model_name: bool = False
