"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.
    Defines scenario-related structures returned by the Insight 5 REST API.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from typing import Optional, Literal, List, Iterable, Union, Tuple, Dict
import sys

from .config import InsightApiBaseModel
from .references import Reference

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self


class ScenarioSummary(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Scenarios.html?scroll=_components_schemas_ScenarioSummary """
    execution_duration: Optional[int] = None
    execution_finished: Optional[str] = None
    execution_mode: Optional[str] = None
    execution_started: Optional[str] = None
    execution_user: Optional[Reference] = None
    model_data_version: Optional[int] = None
    model_status: Optional[str] = None
    objective: Optional[float] = None
    problem_status: Optional[str] = None
    reserved_for_job: Optional[bool] = None
    state: str = 'UNLOADED'


class Scenario(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Scenarios.html?scroll=_components_schemas_Scenario """
    app: Reference
    created: str
    id: str
    name: str
    object_type: Literal['SCENARIO'] = 'SCENARIO'
    owner: Reference
    parent: Reference
    path: str
    scenario_type: str
    share_status: str
    summary: ScenarioSummary = ScenarioSummary()


class ScenarioUpdateRequest(InsightApiBaseModel):
    """ Version of Scenario model containing only the fields that can be updated, and makes them Optional """
    name: Optional[str] = None
    owner: Optional[Reference] = None
    share_status: Optional[str] = None


class ScenarioCreationRequest(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Scenarios.html?scroll=_components_schemas_ScenarioCreationRequest """
    name: str
    parent: Optional[Reference] = None
    scenario_type: Optional[str] = None
    source_scenario: Optional[Reference] = None


class ArrayFilter(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Scenarios.html?scroll=_components_schemas_ArrayFilter """
    entity_name: str
    filter_id: str
    index_filters: Dict[str, List]


class ScenarioDataQuery(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Scenarios.html?scroll=_components_schemas_ScenarioDataQuery """
    entity_names: List[str]
    filters: Optional[List[ArrayFilter]] = None


class EntityData(InsightApiBaseModel):
    """ Data about a single entity of a scenario. Not documented in Insight REST API. """
    entity_name: str
    #
    value: Optional[Union[int, str, float, bool]] = None
    #
    values: Optional[List] = None
    #
    array: Optional[Dict] = None
    array_size: Optional[int] = None
    #
    filter_id: Optional[str] = None


class ScenarioData(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Scenarios.html?scroll=_components_schemas_ScenarioData """
    entities: Dict[str, EntityData]  #
    summary: Optional[ScenarioSummary] = None

    @classmethod
    def from_entity_data(cls, entities: Iterable[EntityData], summary: Optional[ScenarioSummary] = None) -> Self:
        """ Build a ScenarioData from the given iterable of entities (useful during tests) """
        return ScenarioData(entities={e.entity_name: e for e in entities}, summary=summary)


class ArrayElement(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Scenarios.html?scroll=_components_schemas_ArrayElement """
    key: Tuple[Union[str, int, bool], ...]
    value: Union[str, int, bool, float]


class ArrayDelta(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Scenarios.html?scroll=_components_schemas_ArrayDelta """
    add: Optional[List[ArrayElement]] = None
    remove: Optional[List[Tuple[Union[str, int, bool], ...]]] = None


class SetDelta(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Scenarios.html?scroll=_components_schemas_SetDelta """
    add: Optional[Union[List[str], List[int], List[bool]]] = None
    remove: Optional[Union[List[str], List[int], List[bool]]] = None


class EntityDelta(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Scenarios.html?scroll=_components_schemas_EntityDelta """
    entity_name: str
    array_delta: Optional[ArrayDelta] = None
    set_delta: Optional[SetDelta] = None
    value: Optional[Union[int, str, float, bool]] = None


class ScenarioDataModification(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Scenarios.html?scroll=_components_schemas_ScenarioDataModification """
    deltas: List[EntityDelta]
    force_load: bool = False
