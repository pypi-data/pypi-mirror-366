"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.
    Defines folder-related structures returned by the Insight 5 REST API.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from typing import Optional, Literal

from .config import InsightApiBaseModel
from .references import Reference


class Folder(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Folders.html?scroll=_components_schemas_Folder """
    id: str
    object_type: Literal['FOLDER'] = 'FOLDER'
    app: Reference
    name: str
    owner: Reference
    parent: Reference
    path: str
    share_status: str


class FolderUpdateRequest(InsightApiBaseModel):
    """ Version of Folder model containing only the fields that can be updated, and makes them Optional """
    name: Optional[str] = None
    owner: Optional[Reference] = None
    share_status: Optional[str] = None


class FolderCreationRequest(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Folders.html?scroll=_components_schemas_FolderCreationRequest """
    name: str
    parent: Reference
