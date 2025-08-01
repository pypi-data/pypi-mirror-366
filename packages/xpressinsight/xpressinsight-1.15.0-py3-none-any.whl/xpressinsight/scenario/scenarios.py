"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly. This defines functions and classes for accessing Insight
    scenario information through the REST interface.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
# pylint: disable=protected-access,too-many-instance-attributes,too-many-arguments,too-few-public-methods

from abc import ABC
from dataclasses import dataclass
from datetime import datetime, timedelta
import sys
from typing import Optional, Sequence, BinaryIO, TextIO, Union

from . import models
from .attachments import InsightAttachOperations, Attachment, AttachmentUpdate
from .common import (Reference, ShareStatus, parse_insight_enum_value, parse_insight_datetime, ObjectType,
                     get_rest_resource_name)
from ..type_checking import XiEnum

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self


class ModelStatus(XiEnum):
    """
    Enumeration of the possible states a scenario can have after execution.

    Attributes
    ----------

    OK : str
        Model ran without error.
    BREAK : str
        Execution interrupted on a breakpoint.
    ERROR : str
        Runtime error.
    EXIT : str
        Termination via nonzero exit(code).
    INSTR : str
        Invalid instruction.
    IOERR : str
        I/O error.
    LICERR : str
        License error.
    MATHERR : str
        Mathematical error.
    NA : str
        Not applicable.
    NIFCT : str
        Execution interrupted during a native function call.
    NULL : str
        Null dereference error.
    PROB : str
        Error opening or closing a problem.
    STOP : str
        Execution interrupted.
    UNKNOWN : str
        Unknown execution state.
    UNKN_PF : str
        Call to unknown procedure or function.
    UNKN_SYS : str
        Call to unknown system function.
    """
    OK = "OK"
    BREAK = "BREAK"
    ERROR = "ERROR"
    EXIT = "EXIT"
    INSTR = "INSTR"
    IOERR = "IOERR"
    LICERR = "LICERR"
    MATHERR = "MATHERR"
    NA = "NA"
    NIFCT = "NIFCT"
    NULL = "NULL"
    PROB = "PROB"
    STOP = "STOP"
    UNKNOWN = "UNKNOWN"
    UNKN_PF = "UNKN_PF"
    UNKN_SYS = "UNKN_SYS"


class ProblemStatus(XiEnum):
    """
    Enumeration of the possible states an optimization problem can have.

    Attributes
    ----------

    INFEASIBLE : str
        Problem is infeasible.
    NA : str
        Not applicable.
    OPTIMAL : str
        Optimal solution has been found.
    OTHER : str
        Problem is in some other state.
    SOLUTION : str
        Feasible solution has been found, but not proved optimal.
    UNBOUNDED : str
        Problem is unbounded.
    UNFINISHED : str
        Solve was interrupted before completion.
    UNKNOWN : str
        Problem state is not known.
    """
    INFEASIBLE = "INFEASIBLE"
    NA = "NA"
    OPTIMAL = "OPTIMAL"
    OTHER = "OTHER"
    SOLUTION = "SOLUTION"
    UNBOUNDED = "UNBOUNDED"
    UNFINISHED = "UNFINISHED"
    UNKNOWN = "UNKNOWN"


class ScenarioDataState(XiEnum):
    """
    Enumeration of the possible states that a scenario's entity data can be in.

    Attributes
    ----------

    LOADED : str
        Input data is available but not results.
    RESULTS : str
        Input and results are both available.
    RESULTS_DIRTY : str
        Input and results are both available, but inputs have been modified since results were captured.
    UNLOADED : str
        Neither input nor results are available.
    """
    LOADED = 'LOADED'
    RESULTS = 'RESULTS'
    RESULTS_DIRTY = 'RESULTS_DIRTY'
    UNLOADED = 'UNLOADED'


@dataclass
class ScenarioSummary:
    """
    Summary of the state of a scenario, its data, and the most recent job that executed it.

    Attributes
    ----------
    execution_mode : str
        The execution mode of the last execution.
    duration : timedelta
        The duration of the last execution of the scenario
    user : Reference
        The user that last executed this scenario.
    data_version : int
        The version number of the model data.
    data_state : ScenarioDataState
        The state that scenario data is in.
    status : ModelStatus
        The model status of the last execution of this scenario.
    problem_status : ProblemStatus
        The problem status of the lat execution of this scenario.
    start_time : datetime
        When this scenario last started loading or executing.
    finish_time : datetime
        When this scenario last started loading or executing.

    See Also
    --------
    scenario.Scenario
    """
    data_state: ScenarioDataState
    execution_mode: Optional[str] = None
    duration: Optional[timedelta] = None
    user: Optional[Reference] = None
    data_version: Optional[int] = None
    status: Optional[ModelStatus] = None
    problem_status: Optional[ProblemStatus] = None
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None

    @classmethod
    def _from_rest_api_model(cls, src: Optional[models.ScenarioSummary]) -> Optional[Self]:
        if src is None:
            return None

        # noinspection PyProtectedMember
        return ScenarioSummary(
            execution_mode=src.execution_mode,
            duration=None if src.execution_duration is None else timedelta(milliseconds=src.execution_duration),
            user=Reference._from_rest_api_model(src.execution_user),
            data_version=src.model_data_version,
            data_state=parse_insight_enum_value(ScenarioDataState, src.state),
            status=parse_insight_enum_value(ModelStatus, src.model_status),
            problem_status=parse_insight_enum_value(ProblemStatus, src.problem_status),
            start_time=parse_insight_datetime(src.execution_started),
            finish_time=parse_insight_datetime(src.execution_finished)
        )


@dataclass
class Scenario:
    """
    Information about a single scenario.

    Attributes
    ----------
    id : str
        The ID of the scenario.
    created : datetime
        The date and time the scenario was first created.
    owner : Reference
        Information about the user that owns the scenario.
    app : Reference
        Information about the app that owns the scenario.
    parent : Reference
        Information about the folder in which the scenario resides.
    name : str
        Name of the scenario.
    path : str
        Absolute path of the scenario.
    type : str
        The scenario's custom type, if it has one, otherwise `SCENARIO`.
    share_status : ShareStatus
        The share status of the scenario.
    summary : ScenarioSummary, optional
        Summary of the state of the scenario, its data, and the most recent job that executed it.

    See Also
    --------
    scenario.ScenarioSummary
    """
    id: str
    created: datetime
    owner: Reference
    app: Reference
    parent: Reference
    name: str
    path: str
    type: str
    share_status: ShareStatus
    summary: ScenarioSummary

    @classmethod
    def _from_rest_api_model(cls, src: models.Scenario) -> Self:
        # noinspection PyProtectedMember
        return Scenario(
            id=src.id,
            created=parse_insight_datetime(src.created),
            owner=Reference._from_rest_api_model(src.owner),
            app=Reference._from_rest_api_model(src.app),
            parent=Reference._from_rest_api_model(src.parent),
            name=src.name,
            path=src.path,
            type=src.scenario_type,
            share_status=parse_insight_enum_value(ShareStatus, src.share_status),
            summary=ScenarioSummary._from_rest_api_model(src.summary)
        )


# noinspection PyProtectedMember
class InsightScenarioOperations(InsightAttachOperations, ABC):
    """
    Implementation of calls to scenario-related endpoints in the Insight REST API.
    """
    def get_scenario(self, scenario_id: str) -> Scenario:
        """
        Get the scenario record for the scenario with the given ID.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario to query.

        Returns
        -------
        scenario : Scenario
            Information about the scenario with the requested ID.

        Raises
        ------
        scenario.ItemNotFoundError
            If there is no scenario with this ID, or the REST API client credentials do not have permission to access
            it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     scenario = client.get_scenario('570b9100-46e3-4643-baee-2e24aa538f25')
        ...     print(f'Found scenario {scenario.name} with path {scenario.path}')
        """
        scenario = self._make_json_request(
            method='GET',
            path=['api', 'scenarios', scenario_id],
            response_type=models.Scenario
        )

        # noinspection PyProtectedMember
        return Scenario._from_rest_api_model(scenario)

    def create_scenario(self,
                        name: str,
                        parent: Reference,
                        scenario_type: Optional[str] = None) -> Scenario:
        """
        Create a new scenario within an app.

        Parameters
        ----------
        name : str
            The name for the scenario. A suffix will be applied to ensure the name is unique among
            its siblings.
        parent : Reference
            A Reference of type `FOLDER` containing the ID of the folder in which to create the scenario, or a
            reference of type `APP` containing the app ID if the scenario is to be created in the app root folder.
        scenario_type : str, optional
            The type of the scenario to create, as defined by the app. If none is specified, default to `SCENARIO`.

        Returns
        -------
        scenario : Scenario
            Information about the newly-created scenario.

        Raises
        ------
        scenario.InsightServerError
            If the scenario could not be created in the requested location, the REST client credentials do not have
            permission to perform this operation, or there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     FOLDER_ID = '570b9100-46e3-4643-baee-2e24aa538f25'
        ...     scenario = client.create_scenario(name='My Scenario',
        ...         parent=ins.Reference.to_folder(FOLDER_ID))
        ...     print(f'Created scenario {scenario.name} with ID {scenario.id}')

        See Also
        --------
        scenario.InsightRestClient.clone_scenario
        """
        if parent.type not in (ObjectType.FOLDER, ObjectType.APP):
            raise ValueError(f'Unexpected parent type "{parent.type.name}"')

        creation_request = models.ScenarioCreationRequest(
            name=name,
            parent=parent._to_rest_api_model(),
            scenario_type=scenario_type
        )

        scenario = self._make_json_request(
            method='POST',
            path=['api', 'scenarios'],
            request_body=creation_request,
            response_type=models.Scenario,
            expected_status_code=201
        )

        # noinspection PyProtectedMember
        return Scenario._from_rest_api_model(scenario)

    def clone_scenario(self,
                       name: str,
                       source_scenario_id: str,
                       parent: Optional[Reference] = None) -> Scenario:
        """
        Create a copy of an existing scenario within an app.

        Parameters
        ----------
        name : str
            The name for the scenario. A suffix will be applied to ensure the name is unique among its siblings.
        source_scenario_id : str
            The ID of the scenario to clone.
        parent : Reference, optional
            A Reference of type `FOLDER` containing the ID of the folder in which to create the new scenario, or a
            reference of type `APP` containing the app ID if the new scenario is to be created in the app root folder.
            If not given, the new scenario is created in the same folder as the source.

        Returns
        -------
        scenario : Scenario
            Information about the newly-created scenario.

        Raises
        ------
        scenario.InsightServerError
            If the scenario could not be created in the requested location, the REST client credentials do not have
            permission to perform this operation, or there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     SOURCE_SCENARIO_ID = '95a2a7de-344b-4e37-ad02-9339ba42bfe0'
        ...     FOLDER_ID = '570b9100-46e3-4643-baee-2e24aa538f25'
        ...     scenario = client.clone_scenario(name='My Scenario',
        ...         source_scenario_id=SOURCE_SCENARIO_ID,
        ...         parent=ins.Reference.to_folder(FOLDER_ID))
        ...     print(f'Created scenario {scenario.name} with ID {scenario.id}')

        See Also
        --------
        scenario.InsightRestClient.create_scenario
        """
        if parent is not None and parent.type not in (ObjectType.FOLDER, ObjectType.APP):
            raise ValueError(f'Unexpected parent type "{parent.type.name}"')

        creation_request = models.ScenarioCreationRequest(
            name=name,
            source_scenario=models.Reference(id=source_scenario_id, object_type=ObjectType.SCENARIO),
            parent=None if parent is None else parent._to_rest_api_model()
        )

        scenario = self._make_json_request(
            method='POST',
            path=['api', 'scenarios'],
            request_body=creation_request,
            response_type=models.Scenario,
            expected_status_code=201
        )

        # noinspection PyProtectedMember
        return Scenario._from_rest_api_model(scenario)

    def delete_scenario(self, scenario_id: str) -> None:
        """
        Delete an existing scenario within an app.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario to delete.

        Raises
        ------
        scenario.ItemNotFoundError
            If there is no scenario with this ID, or the REST API client credentials do not have permission to access
            it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.delete_scenario('570b9100-46e3-4643-baee-2e24aa538f25')
        """
        self._make_json_request(
            method='DELETE',
            path=['api', 'scenarios', scenario_id],
            response_type=None,
            expected_status_code=204
        )

    def move_scenario(self, scenario_id: str, new_parent: Reference) -> None:
        """
        Move a scenario to a different folder or the app root.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario to move.
        new_parent : Reference
            A Reference to either a folder in the same app as the scenario, or the app ID in which the scenario
            resides if moving to the app root.

        Raises
        ------
        scenario.InsightServerError
            If there is an issue performing this request or communicating with the Insight server.

        Examples
        --------
        To move a scenario to a different folder:

        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     DESTINATION_ID='f3336733-5cf9-49fc-84f0-3e7ee80df98e'
        ...     client.move_scenario('570b9100-46e3-4643-baee-2e24aa538f25',
        ...                          new_parent=Reference.to_folder(DESTINATION_ID))
        """
        if new_parent.type not in (ObjectType.FOLDER, ObjectType.APP):
            raise ValueError(f'Unexpected parent type "{new_parent.type.name}"')

        self._make_json_request(
            path=['api', get_rest_resource_name(new_parent.type), new_parent.id, 'children'],
            method='POST',
            request_body=models.Reference(
                id=scenario_id,
                object_type='SCENARIO'
            ),
            response_type=None
        )

    def rename_scenario(self, scenario_id: str, new_name: str) -> None:
        """
        Rename an existing scenario

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario to rename.
        new_name : str
            The new name for the scenario.

        Raises
        ------
        scenario.InsightServerError
            If there is an issue performing this request or communicating with the Insight server.

        Examples
        --------
        Example of updating the name of a scenario.

        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.rename_scenario('570b9100-46e3-4643-baee-2e24aa538f25',
        ...                            'New Forecast')
        """
        self._make_json_request(
            path=['api', 'scenarios', scenario_id],
            method='PATCH',
            request_body=models.ScenarioUpdateRequest(name=new_name),
            response_type=None
        )

    def set_scenario_owner(self, scenario_id: str, new_owner_id: str, new_share_status: Optional[ShareStatus] = None
                           ) -> None:
        """
        Update scenario owner and (optionally) share status.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario to update.
        new_owner_id : str
            The ID of the user who should become the scenario owner.
        new_share_status : ShareStatus, optional
            The new share status of the scenario, if this is also being updated.

        Raises
        ------
        scenario.InsightServerError
            If there is an issue performing this request or communicating with the Insight server.
        """
        self._make_json_request(
            path=['api', 'scenarios', scenario_id],
            method='PATCH',
            request_body=models.ScenarioUpdateRequest(owner=models.Reference(id=new_owner_id, object_type='USER'),
                                                      share_status=(None if new_share_status is None
                                                                    else new_share_status.name)),
            response_type=None
        )

    def set_scenario_share_status(self, scenario_id: str, new_share_status: ShareStatus) -> None:
        """
        Update scenario share status.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario to update.
        new_share_status : ShareStatus
            The new share status of the scenario.

        Raises
        ------
        scenario.InsightServerError
            If there is an issue performing this request or communicating with the Insight server.
        """
        self._make_json_request(
            path=['api', 'scenarios', scenario_id],
            method='PATCH',
            request_body=models.ScenarioUpdateRequest(share_status=new_share_status.name),
            response_type=None
        )

    def get_scenario_run_log(self, scenario_id: str) -> str:
        """
        Get the run log captured during the completed scenario execution.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario to query.

        Returns
        -------
        run_log : str
            The full run log of the scenario

        Raises
        ------
        scenario.ItemNotFoundError
            If there is no scenario with this ID, or it did not have a completed run log, or the REST API client
            credentials do not have permission to access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     SCENARIO_ID = '570b9100-46e3-4643-baee-2e24aa538f25'
        ...     run_log = client.get_scenario_run_log(SCENARIO_ID)
        ...     print(run_log)

        Notes
        -----
        This function cannot be used to read the run log of a currently executing scenario.
        """
        return self._make_json_request(
            path=['api', 'scenarios', scenario_id, 'run-log'],
            method='GET',
            response_type=str
        )

    def get_scenario_attachment_info(self, scenario_id: str, attachment_id: str) -> Attachment:
        """
        Get information about a given scenario attachment.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario on which the attachment resides.
        attachment_id : str
            The ID of the attachment.

        Returns
        -------
        attachment : Attachment
            Information about the scenario attachment with the requested ID.

        Raises
        ------
        scenario.ItemNotFoundError
            If the scenario or attachment cannot be found, or the REST API client credentials do not have permission
            to access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     info = client.get_scenario_attachment_info(
        ...         scenario_id='570b9100-46e3-4643-baee-2e24aa538f25',
        ...         attachment_id='ae91efb6-387c-442d-b27d-655fe42a9ad4')
        ...     print(f'Attachment name is {info.name}')
        """
        return self._get_attachment_info(['api', 'scenarios', scenario_id, 'attachments'], attachment_id)

    def get_all_scenario_attachment_info(self, scenario_id: str) -> Sequence[Attachment]:
        """
        Get information about all the attachments on the given scenario.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario for which to query attachments.

        Returns
        -------
        attachments : Sequence[Attachment]
            Information about the scenario attachments on the given scenario.

        Raises
        ------
        scenario.ItemNotFoundError
            If the scenario does not exist, or the REST API client credentials do not have permission to access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     infos = client.get_all_scenario_attachment_info(
        ...         scenario_id='570b9100-46e3-4643-baee-2e24aa538f25')
        ...     for info in infos:
        ...         print(f'Found attachment named {info.name}')
        """
        return self._get_all_attachment_info(['api', 'scenarios', scenario_id, 'attachments'])

    def get_scenario_attachment(self, scenario_id: str, attachment_id: str,
                                destination: Union[str, TextIO, BinaryIO],
                                encoding: Optional[str] = 'utf-8') -> None:
        """
        Download the indicated scenario attachment.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario on which the attachment resides.
        attachment_id : str
            The ID of the attachment.
        destination : Union[str, TextIO, BinaryIO]
            Where to save the attachment content. This may be the name of a local file, or any file-like object.
        encoding : str, default 'utf-8'
            The character encoding to use when `destination` is of type `TextIO`. Defaults to `utf-8`.

        Raises
        ------
        scenario.ItemNotFoundError
            If the scenario or attachment does exist, or the REST API client credentials do not have permission to
            access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.get_scenario_attachment(
        ...         scenario_id='570b9100-46e3-4643-baee-2e24aa538f25',
        ...         attachment_id='ae91efb6-387c-442d-b27d-655fe42a9ad4',
        ...         destination='my_local_file.json')
        """
        return self._get_attachment(['api', 'scenarios', scenario_id, 'attachments'], attachment_id,
                                    destination,
                                    encoding=encoding)

    def put_scenario_attachment(self, scenario_id: str, attachment_name: str,
                                source: Union[str, TextIO, BinaryIO],
                                tag_name: Optional[str] = None,
                                overwrite: bool = False,
                                encoding: Optional[str] = 'utf-8') -> Attachment:
        """
        Upload a scenario attachment, either creating a new attachment or overwriting an existing one of the
        same name.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario on which to save the attachment.
        attachment_name : str
            The name to give the attachment (for example, `"factories.csv"`).
        source : Union[str, TextIO, BinaryIO]
            Where to read the attachment content. This may be the name of a local file, or any file-like object.
        tag_name : str, optional
            The name of a tag to give the attachment, if any.
        overwrite : bool, default False
            If set to `True`, the new attachment overwrites any existing scenario attachment that has the same name.
            If `False`, the new attachment will be given a different name if there is an existing attachment
            with the same name.
        encoding : str, default 'utf-8'
            The character encoding to use when `source` is of type `TextIO`. Defaults to `utf-8`.

        Returns
        -------
        attachment : Attachment
            Information about the new or updated scenario attachment record.

        Raises
        ------
        scenario.ItemNotFoundError
            If the scenario does not exist, or the REST API client credentials do not have permission to
            access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.put_scenario_attachment(
        ...         scenario_id='570b9100-46e3-4643-baee-2e24aa538f25',
        ...         attachment_name='factories.csv',
        ...         source='factories.csv')
        """
        return self._put_attachment(['api', 'scenarios', scenario_id, 'attachments'], attachment_name,
                                    source,
                                    tag_name=tag_name,
                                    overwrite=overwrite,
                                    encoding=encoding)

    def set_scenario_attachment_info(self, scenario_id: str, attachment_id: str,
                                     updated_info: Union[Attachment, AttachmentUpdate]) -> None:
        """
        Updates the filename, description, tags or 'hidden' flag for the given scenario attachment.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario on which the attachment resides.
        attachment_id : str
            The ID of the attachment.
        updated_info : Union[Attachment, AttachmentUpdate]
            The attachment info to update. Only the fields you want to change should be populated.

        Raises
        ------
        scenario.ItemNotFoundError
            If the scenario or attachment does not exist, or the REST API client credentials do not have permission to
            access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.put_scenario_attachment(
        ...         scenario_id='570b9100-46e3-4643-baee-2e24aa538f25',
        ...         attachment_id='ae91efb6-387c-442d-b27d-655fe42a9ad4',
        ...         updated_info=ins.AttachmentUpdate(tags=['monthly', 'approved']))
        """
        return self._set_attachment_info(['api', 'scenarios', scenario_id, 'attachments'], attachment_id, updated_info)

    def delete_scenario_attachment(self, scenario_id: str, attachment_id: str) -> None:
        """
        Delete the specified scenario attachment.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario on which the attachment resides.
        attachment_id : str
            The ID of the attachment.

        Raises
        ------
        scenario.ItemNotFoundError
            If the scenario or attachment does not exist, or the REST API client credentials do not have permission to
            access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.delete_scenario_attachment(
        ...         scenario_id='570b9100-46e3-4643-baee-2e24aa538f25',
        ...         attachment_id='ae91efb6-387c-442d-b27d-655fe42a9ad4')
        """
        return self._delete_attachment(['api', 'scenarios', scenario_id, 'attachments'], attachment_id)
