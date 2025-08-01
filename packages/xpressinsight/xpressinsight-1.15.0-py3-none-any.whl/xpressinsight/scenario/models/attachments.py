"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.
    Defines attachment-related structures returned by the Insight 5 REST API.

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


class Attachment(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Attachments.html?scroll=_components_schemas_Attachment """
    app: Reference
    description: str = ''
    filename: str
    hidden: bool = False
    id: str
    last_modified: str
    last_modified_by: Reference
    name: str
    object_type: Literal['ATTACHMENT'] = 'ATTACHMENT'
    parent: Reference
    size: int = 0
    tags: List[str] = []


class AttachmentUpdateRequest(InsightApiBaseModel):
    """ Version of Attachment model used for updates - contains only fields that can be updated, and makes them
        Optional """
    description: Optional[str] = None
    filename: Optional[str] = None
    hidden: Optional[bool] = None
    tags: Optional[List[str]] = None


class AttachmentTag(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Attachments.html?scroll=_components_schemas_AttachmentTag """
    description: str = ''
    mandatory: bool = False
    multi_file: bool = False
    name: str
