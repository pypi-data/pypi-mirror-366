"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.
    Defines app-related structures returned by the Insight 5 REST API.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from typing import Optional, Literal, List, Dict

from .config import InsightApiBaseModel
from .references import Reference


class AppModel(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Apps.html?scroll=_components_schemas_AppModel """
    data_version: int = 0
    name: str = ''
    version: str = '0.0.0'


class App(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Apps.html?scroll=_components_schemas_App """
    id: str
    object_type: Literal['APP'] = 'APP'
    model: AppModel = AppModel()
    name: str
    path: str


class AppMember(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Apps.html?scroll=_components_schemas_AppMember """
    id: str
    object_type: Literal['APP_MEMBER'] = 'APP_MEMBER'
    authorities: List[str] = []
    authority_groups: List[Reference] = []
    first_name: str = ''
    last_name: str = ''
    name: str = ''


class AppCreationResponse(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Apps.html?scroll=_components_schemas_AppCreationResponse """
    app: App
    messages: List[str] = []


class ModelEntity(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ see https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Apps.html?scroll=_components_schemas_ModelEntity """
    #
    name: str
    data_type: str
    element_type: Optional[str] = None
    index_sets: Optional[List[str]] = None


class ModelSchema(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ see https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Apps.html?scroll=_components_schemas_ModelSchema """
    #
    entities: Dict[str, ModelEntity]
    object_type: Literal['MODEL_SCHEMA'] = 'MODEL_SCHEMA'
