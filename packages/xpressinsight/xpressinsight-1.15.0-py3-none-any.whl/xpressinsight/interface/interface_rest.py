"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Online interface definition.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2025 Fair Isaac Corporation. All rights reserved.
"""
import os
import re
import sys
import threading
from datetime import datetime, timedelta, timezone
from functools import cached_property
from tempfile import TemporaryDirectory
from typing import Dict, Generator, List, Optional, Union, Type, Iterable

from . import apprunner_rest_client as xi_rest
from .interface_errors import (
    _raise_interface_error,
    ScenarioNotFoundError,
    InvalidEntitiesError
)
from .attach_errors import (
    AttachStatus,
    AttachNotFoundError,
    AttachFilenameInvalidError,
    AttachDescriptionInvalidError,
    AttachAlreadyExistsError,
    AttachTooLargeError,
    TooManyAttachError,
    AttachTagsInvalidError,
    SeveralAttachFoundError,
    RuntimeAttachError,
)
from .interface import (
    Attachment,
    AttachmentRules,
    AttachTag,
    AttachTagUsage,
    ItemInfo,
    Metric,
    ObjSense,
    InsightContext,
    InsightDmpContext,
    SolutionDatabase,
    ResourceLimits,
    SCENARIO_DATA_CONTAINER,
)
from .interface_base import AppInterfaceBase, handle_attach_errors
from ..data_connectors import DataConnector
from ..entities import Entity
from ..entities_config import EntitiesContainer
from ..exec_mode import ExecMode
from ..scenario import InsightRestClient
from ..slow_tasks_monitor import SlowTasksMonitor
from ..type_checking import XiEnum

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override

ERROR_MSG_PROD_MODE_METHOD = 'The method "{}" cannot be used in production mode.'
ATTACH_STATUS_PREFIX = "INSIGHT_ATTACH_"


class RequestStatus(XiEnum):
    """
    Indicates the status of the most recent attempt to call a generic AppInterface function.

    Attributes
    ----------
    OK: int
        The operation completed successfully.
    ERROR: int
        An error occurred.

    Notes
    -----
    This enum is only used internally.
    """

    OK = 0
    ERROR = 1


def parse_status_str(status_str: str, prefix: str, enum_type: Type[XiEnum]) -> Union[RequestStatus, AttachStatus]:
    """
    Convert a string like `"INSIGHT_OK"` into enum value `RequestStatus.OK`.
    """

    #
    if not status_str.startswith(prefix):
        raise ValueError(f'Invalid {enum_type.__name__} string prefix: "{status_str}". Expected: "{prefix}".')

    #
    short_status_str = status_str[len(prefix):]

    if short_status_str not in enum_type.__members__:
        raise ValueError(f'Unknown {enum_type.__name__}: "{status_str}".')

    return enum_type[short_status_str]


def parse_request_status(request_status_str: str) -> RequestStatus:
    """
    Convert a string like `"INSIGHT_OK"` into enum value `RequestStatus.OK`.
    """
    return parse_status_str(request_status_str, "INSIGHT_", RequestStatus)


def parse_attach_status(attach_status_str: str) -> AttachStatus:
    """
    Convert a string like `"INSIGHT_ATTACH_INVALID_FILENAME"` into enum value `AttachStatus.INVALID_FILENAME`.
    """
    return parse_status_str(attach_status_str, "INSIGHT_ATTACH_", AttachStatus)


def check_for_attach_error(response_or_status: Union[dict, str], operation_name: str) -> None:
    """
    Given the response returned by an attachment operation, check the status as given in the
    'status' entry and raise an appropriate error if this is not OK.  The 'operation name'
    string will be used in the error message.

    Parameters
    ----------
    response_or_status: dict or str
        Either a JSON document returned by the attachment request, or string containing the attachment
        status value.
    operation_name: str
        The name of the operation, e.g. "list attachment tags"; for use in error messages.
    """
    attach_status = parse_attach_status(response_or_status["status"] if isinstance(response_or_status, dict)
                                        else response_or_status)
    if attach_status == AttachStatus.OK:
        return
    if attach_status == AttachStatus.NOT_FOUND:
        raise AttachNotFoundError(f'Failed to {operation_name}; attachment was not found.')
    if attach_status == AttachStatus.INVALID_FILENAME:
        raise AttachFilenameInvalidError(f'Failed to {operation_name}; attachment filename was invalid.')
    if attach_status == AttachStatus.INVALID_DESCRIPTION:
        raise AttachDescriptionInvalidError(f'Failed to {operation_name}; attachment description was invalid.')
    if attach_status == AttachStatus.ALREADY_EXISTS:
        raise AttachAlreadyExistsError(f'Failed to {operation_name}; attachment already exists.')
    if attach_status == AttachStatus.TOO_LARGE:
        raise AttachTooLargeError(f'Failed to {operation_name}; attachment is too large.')
    if attach_status == AttachStatus.TOO_MANY:
        raise TooManyAttachError(f'Failed to {operation_name}; too many attachments.')
    if attach_status == AttachStatus.INVALID_TAGS:
        raise AttachTagsInvalidError(f'Failed to {operation_name}; attachment tags were invalid.')
    if attach_status == AttachStatus.SEVERAL_FOUND:
        raise SeveralAttachFoundError(f'Failed to {operation_name}; several matching attachments found.')
    raise RuntimeAttachError(f'Failed to {operation_name} with status {attach_status.name}.')


#
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def _attachment_from_dict(attachment: Dict) -> Attachment:
    return Attachment(
        filename=attachment["filename"],
        description=attachment["description"],
        tags=attachment["tags"],
        size=attachment["size"],
        last_modified_user=attachment["lastModifiedUser"],
        last_modified_date=datetime.strptime(attachment["lastModifiedDate"], DATETIME_FORMAT),
        hidden=attachment["hidden"],
    )


def _item_info_from_dict(item_info: Dict) -> ItemInfo:
    return ItemInfo(
        id=item_info["id"],
        type=item_info["type"],
        name=item_info["name"],
        path=item_info["path"],
        parent_path=item_info["parentpath"]
    )


def _verify_safe_mosel_filename(filename: Optional[str]):
    """ Given a filename, verify it is 'safe' to pass to Mosel, and is not an 'extended' Mosel filename reading/writing
        an IO driver.
        Raises ValueError if filename is not safe. """
    if re.match(r"^[^:][^:]+:.*", filename):
        raise ValueError(f"Filename '{filename}' contains a Mosel I/O Driver, which may not be passed from Python apps")


#
# pylint: disable-next=too-many-public-methods
class AppRestInterface(AppInterfaceBase):
    """
    This class represents the Xpress Insight application interface. Use this interface to access attachments
    and metadata like the scenario ID.
    """

    _api_client: Optional[xi_rest.ApiClient]

    #
    #
    #
    # pylint: disable-next=too-many-locals
    def __init__(
            self,
            rest_port: int,
            rest_token: str,
            app_id: str = "",
            app_name: str = "",
            scenario_id: str = "",
            scenario_name: str = "",
            scenario_path: str = "",
            exec_mode: str = ExecMode.NONE,  #
            test_mode: bool = False,
            test_attach_dir: str = "",
            test_cfile_path: str = "",
            work_dir: str = os.path.join("work_dir", "insight"),
            app=None,
            slow_tasks_monitor: Optional[SlowTasksMonitor] = None,
            raise_attach_exceptions: Optional[bool] = None,
    ) -> None:

        super().__init__(app_id=app_id,
                         app_name=app_name,
                         scenario_id=scenario_id,
                         scenario_name=scenario_name,
                         scenario_path=scenario_path,
                         exec_mode=exec_mode,
                         test_mode=test_mode,
                         test_attach_dir=test_attach_dir,
                         test_cfile_path=test_cfile_path,
                         work_dir=work_dir,
                         app=app,
                         slow_tasks_monitor=slow_tasks_monitor,
                         raise_attach_exceptions=raise_attach_exceptions)

        self._api_client = None
        self._init_rest(rest_port, rest_token)
        self._progress_entities_lock = threading.Lock()

    def _init_rest(self, port: int, token: str):
        configuration = xi_rest.Configuration(
            host=f"http://localhost:{port}",
            api_key={"token": f"token={token}"},
        )

        if self._api_client:
            self._api_client.close()
            self._api_client = None

        self._api_client = xi_rest.ApiClient(configuration)
        self._api = xi_rest.DefaultApi(self._api_client)

        #
        #
        #
        #

    @override
    @property
    def work_dir(self) -> str:
        return self._work_dir

    def delete_work_dir(self):
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('delete_work_dir'))

    @override
    @property
    def test_mode(self) -> bool:

        return self._test_mode

    #
    @override
    @property
    def exec_mode(self) -> str:
        with self._exec_mode_lock:
            return self._exec_mode

    #
    @override
    @property
    def app_id(self) -> str:

        return self._api.app_id_get()

    #
    @property
    @override
    def app_name(self) -> str:

        return self._api.app_name_get()

    #
    @override
    @property
    def username(self) -> str:

        return self._api.username_get()

    #
    @override
    @cached_property
    def user_id(self) -> str:
        return self._api.user_id_get()

    #

    #

    #
    #


    #
    @override
    @handle_attach_errors(on_error_return=[])
    def list_attach_tags(self) -> List[AttachTag]:
        result = self._api.attachments_tags_get()
        check_for_attach_error(result, operation_name='list attachment tags')
        return [
            AttachTag(
                name=tag["name"],
                description=tag["description"],
                mandatory=tag["mandatory"],
                usage=AttachTagUsage(tag["usage"]),
            )
            for tag in result["tags"]
        ]

    #
    #
    #
    @override
    @handle_attach_errors(on_error_return=None)
    def get_scen_attach(self, filename: str, scenario_path: str = None, *, destination_filename: str = None) -> None:
        if destination_filename:
            _verify_safe_mosel_filename(destination_filename)

        if scenario_path is None:
            scenario_path = ""

        attach_status_str = self._api.scenario_attachment_get(filename, scenariopath=scenario_path,
                                                              dstfilename=destination_filename)
        check_for_attach_error(attach_status_str, operation_name=f'get scenario attachment "{filename}"')

    @override
    @handle_attach_errors(on_error_return=None)
    def put_scen_attach(self, filename: str, overwrite: bool = True, *, source_filename: str = None) -> None:
        if source_filename:
            _verify_safe_mosel_filename(source_filename)

        attach_status_str = self._api.scenario_attachment_put(filename, overwrite, srcfilename=source_filename)
        check_for_attach_error(attach_status_str, operation_name=f'put scenario attachment "{filename}"')

    #
    @override
    @handle_attach_errors(on_error_return=None)
    def delete_scen_attach(self, filename: str) -> None:
        attach_status_str = self._api.scenario_attachment_delete(filename)
        check_for_attach_error(attach_status_str, operation_name=f'delete scenario attachment "{filename}"')

    #
    @override
    @handle_attach_errors(on_error_return=None)
    def rename_scen_attach(self, old_name: str, new_name: str) -> None:
        attach_status_str = self._api.scenario_attachment_rename(old_name, new_name)
        check_for_attach_error(attach_status_str, operation_name=f'rename scenario attachment "{old_name}" '
                                                                 f'to "{new_name}"')

    #
    @override
    @handle_attach_errors(on_error_return=None)
    def set_scen_attach_desc(self, filename: str, description: str) -> None:
        attach_status_str = self._api.scenario_attachment_description_put(
            filename, description=description
        )
        check_for_attach_error(attach_status_str, operation_name=f'set description of scenario '
                                                                 f'attachment "{filename}"')

    #
    @override
    @handle_attach_errors(on_error_return=None)
    def set_scen_attach_tags(self, filename: str, tags: List[str]) -> None:
        attach_status_str = self._api.scenario_attachment_tags_put(filename, tags=tags)
        check_for_attach_error(attach_status_str, operation_name=f'set tags of scenario attachment "{filename}"')

    #
    @override
    @handle_attach_errors(on_error_return=None)
    def set_scen_attach_hidden(self, filename: str, hidden: bool) -> None:
        attach_status_str = self._api.scenario_attachment_hidden_put(filename, hidden=hidden)
        check_for_attach_error(attach_status_str, operation_name=f'update hidden flag of scenario '
                                                                 f'attachment "{filename}"')

    #
    #
    @override
    @handle_attach_errors(on_error_return=[])
    def list_scen_attach(self, scenario_path: str = None) -> List[Attachment]:
        return self.list_scen_attach_by_tag("", scenario_path)

    #
    #
    #
    @override
    @handle_attach_errors(on_error_return=[])
    def list_scen_attach_by_tag(
            self, tag: str, scenario_path: str = None
    ) -> List[Attachment]:
        if scenario_path is None:
            scenario_path = ""

        result = self._api.scenario_attachments_list_get(tag=tag, scenariopath=scenario_path)
        check_for_attach_error(result, operation_name=f'list attachments of scenario "{scenario_path}"')
        return [_attachment_from_dict(a) for a in result["attachments"]]

    #
    @override
    @handle_attach_errors(on_error_return=None)
    def scen_attach_info(self, filename: str) -> Optional[Attachment]:
        result = self._api.scenario_attachment_info_get(filename)
        check_for_attach_error(result, operation_name=f'get info about scenario attachment "{filename}"')
        return _attachment_from_dict(result["attachment"])

    #
    #
    @override
    @handle_attach_errors(on_error_return=None)
    def get_app_attach(self, filename: str, *, destination_filename: str = None) -> None:
        if destination_filename:
            _verify_safe_mosel_filename(destination_filename)

        attach_status_str = self._api.app_attachment_get(filename, dstfilename=destination_filename)
        check_for_attach_error(attach_status_str, operation_name=f'get app attachment "{filename}"')

    #
    @override
    @handle_attach_errors(on_error_return=[])
    def list_app_attach(self) -> List[Attachment]:
        tag = ""
        return self.list_app_attach_by_tag(tag)

    #
    @override
    @handle_attach_errors(on_error_return=[])
    def list_app_attach_by_tag(self, tag: str) -> List[Attachment]:
        result = self._api.app_attachments_list_get(tag)
        check_for_attach_error(result, operation_name='list app attachments')
        return [_attachment_from_dict(a) for a in result["attachments"]]

    #
    @override
    @handle_attach_errors(on_error_return=None)
    def app_attach_info(self, filename: str) -> Optional[Attachment]:
        result = self._api.app_attachment_info_get(filename)
        check_for_attach_error(result, operation_name=f'get info about app attachment "{filename}"')
        return _attachment_from_dict(result["attachment"])

    @override
    @handle_attach_errors(on_error_return=[])
    def get_attachs_by_tag(self, tag: str, *, destination_directory: str = None) -> Optional[List[Attachment]]:
        #
        if destination_directory:
            _verify_safe_mosel_filename(destination_directory)

            if not os.path.exists(destination_directory):
                raise FileNotFoundError(f"Directory '{destination_directory}' not found")

            if not os.path.isdir(destination_directory):
                raise NotADirectoryError(f"Path '{destination_directory}' is not a directory")

        #
        result = self._api.attachments_tags_bytag_get(tag, directory=destination_directory)
        check_for_attach_error(result, operation_name=f'get attachments with tag "{tag}"')
        return [_attachment_from_dict(a) for a in result["attachments"]]

    #
    @override
    @handle_attach_errors(on_error_return=None)
    def get_attach_by_tag(self, tag: str, *, destination_directory: str = None) -> Optional[Attachment]:
        attachments = self.get_attachs_by_tag(tag, destination_directory=destination_directory)
        if len(attachments) == 1:
            return attachments[0]
        if len(attachments) > 1:
            raise SeveralAttachFoundError(f'Found {len(attachments)} attachments with tag "{tag}"')
        return None

    #
    @override
    @handle_attach_errors(on_error_return=[])
    def get_attach_filenames_by_tag(self, tag: str, *, destination_directory: str = None) -> List[str]:
        attachments = self.get_attachs_by_tag(tag, destination_directory=destination_directory)
        return [a.filename for a in attachments]

    #
    @override
    def get_attach_rules(self) -> AttachmentRules:
        rules = self._api.attachments_rules_get()

        return AttachmentRules(
            max_size=rules.maxsize,
            max_attach_count=rules.maxattachcount,
            max_filename_len=rules.maxfilenamelen,
            invalid_filename_chars=rules.invalidfilenamechars,
            max_description_len=rules.maxdescriptionlen,
        )

    @override
    def get_item_info(self, path: str) -> ItemInfo:
        result = self._api.repository_item_info_get(path)
        status = parse_request_status(result["status"])

        if status != RequestStatus.OK:
            _raise_interface_error(f"Could not get item info. (Status: {status})")

        return _item_info_from_dict(result["item_info"])

    @override
    def get_item_infos(self, folder_path: str) -> List[ItemInfo]:
        result = self._api.repository_item_infos_list_get(folder_path)
        status = parse_request_status(result["status"])

        if status != RequestStatus.OK:
            _raise_interface_error(f"Could not get item infos. (Status: {status})")

        return [_item_info_from_dict(item_info) for item_info in result["item_infos"]]

    @override
    def add_item_info(self, item_info: ItemInfo) -> None:
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('add_item_info'))

    @override
    def clear_item_infos(self) -> None:
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('clear_item_infos'))

    #

    #

    @override
    @property
    def scenario_id(self):
        return self._api.scenario_id_get()

    @override
    @property
    def scenario_name(self) -> str:
        return self._api.scenario_name_get()

    @override
    @property
    def scenario_path(self) -> str:
        return self._api.scenario_path_get()

    @override
    @property
    def test_cfile_path(self) -> str:
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('test_cfile_path getter'))

    @test_cfile_path.setter
    def test_cfile_path(self, cfile_path: str):
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('test_cfile_path setter'))

    @override
    @property
    def test_attach_dir(self) -> str:
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('test_attach_dir getter'))

    @test_attach_dir.setter
    def test_attach_dir(self, attach_dir: str):
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('test_attach_dir setter'))

    @override
    @property
    def test_app_attach_dir(self) -> str:
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('test_app_attach_dir getter'))

    @test_app_attach_dir.setter
    def test_app_attach_dir(self, app_attach_dir: str):
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('test_app_attach_dir setter'))

    @override
    @property
    def test_scen_attach_dir(self) -> str:
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('test_scen_attach_dir getter'))

    @test_scen_attach_dir.setter
    def test_scen_attach_dir(self, scen_attach_dir: str):
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('test_scen_attach_dir setter'))

    @override
    def set_attach_tags(self, new_tags: List[AttachTag]):
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('set_attach_tags'))

    @override
    def set_attach_rules(self, new_rules: AttachmentRules):
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('set_attach_rules'))

    @override
    def get_scenario_data(self, scenario_path_or_id: str, scenario_data_class: Type[SCENARIO_DATA_CONTAINER], *,
                          fetch_individual_series=False) -> SCENARIO_DATA_CONTAINER:
        if not issubclass(scenario_data_class, EntitiesContainer):
            raise TypeError("Scenario data class must be decorated with @xi.ScenarioData.")

        entity_data = scenario_data_class()

        #
        with TemporaryDirectory(prefix='.scendata_', dir=self._app.insight.work_dir) as temp_dir:
            #
            data_connector: DataConnector = self._app.app_cfg._insight_worker_data_connector_cls(
                app=self._app,
                data_container=entity_data,
                scenario_path_or_id=scenario_path_or_id,
                parquet_dir=temp_dir,
                fetch_individual_series=fetch_individual_series,
                input_only=False,
                slow_tasks_monitor=self._slow_tasks_monitor)

            #
            data_connector.load_entities(entity_filter=lambda entity: True)

            #
            return entity_data

    def _fetch_scenario_data_parquet(self, scenario_path_or_id: str, output_dir: str,
                                     conversion_description_file: str, input_only: bool):
        """ Request the Insight server to perform the given conversion on entities of the given scenario and write
            to the given directory. """
        try:
            with self._slow_tasks_monitor.task(f'Fetching entity data from scenario `{scenario_path_or_id}`'):
                self._api.scenario_data_get(scenario=scenario_path_or_id, output_dir=output_dir,
                                            tables_descr_file=conversion_description_file, input_only=input_only)
        except xi_rest.ApiException as e:
            if e.status == 404:
                raise ScenarioNotFoundError(e.body) from None

            if e.status == 412:
                raise InvalidEntitiesError(e.body) from None

            if e.status in (500, 503):
                _raise_interface_error(f"Could not get data from Insight scenario '{scenario_path_or_id}' "
                                       f"due to: {e.body}")

            raise e

    @override
    def set_scenario_test_data(self, scenario_path_or_id: str, scenario_data_class: Type[SCENARIO_DATA_CONTAINER],
                               scenario_data: SCENARIO_DATA_CONTAINER):
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('set_scenario_data'))

    @override
    def update(self, metric: Metric, value: Union[float, int, ObjSense]) -> None:
        float_value = value.value if isinstance(value, ObjSense) else float(value)
        self._api.progress_update(metric=metric.value, value=float_value)

    @override
    def reset_progress(self) -> None:
        self._api.progress_reset()

    @override
    def send_progress_update(self) -> None:
        exec_mode = self._app.app_cfg.get_exec_mode(self.exec_mode)

        if exec_mode.send_progress:
            with self._progress_entities_lock:
                #
                self._app.data_connector.save_progress()

                #
                self._api.progress_send()

    @override
    def get_messages(self) -> Generator[str, None, None]:
        while True:
            (msg, status_code, _) = self._api.progress_get_message_with_http_info()

            if status_code == 200:
                yield msg
            else:
                break

    @override
    def put_messages(self, *msgs: str) -> None:
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('put_messages'))

    @override
    @property
    def version(self) -> str:
        return self._api.insight_version_get()

    @version.setter
    def version(self, new_version: str):
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('version setter'))

    @override
    def get_insight_context(self, environment: Optional[str] = None) -> InsightContext:
        try:
            src_context: xi_rest.InsightContext = self._api.insight_context_get(environment or "")
            src_dmp_context: xi_rest.InsightDmpContext = src_context.dmp
            return InsightContext(
                insight_url=src_context.insighturl,
                trace_id=src_context.traceid,
                span_id=src_context.spanid,
                parent_span_id=None if src_context.parentspanid == '' else src_context.parentspanid,
                sampled=None if src_context.sampled == '' else src_context.sampled,
                dmp=None if not src_dmp_context.ispopulated else InsightDmpContext(
                    manager_url=src_dmp_context.managerurl,
                    environment=src_dmp_context.environment,
                    tenant_id=src_dmp_context.tenantid,
                    solution_id=src_dmp_context.solutionid,
                    component_id=src_dmp_context.componentid,
                    component_instance_id=src_dmp_context.compinstid,
                    solution_token=src_dmp_context.soltoken,
                    #
                    #
                    #
                    solution_token_expiry_time=datetime(1970, 1, 1, tzinfo=timezone.utc) +
                                               timedelta(milliseconds=src_dmp_context.soltokenexpiry),
                    solution_token_environment=src_dmp_context.soltokenenv,
                    platform_token=src_dmp_context.pftoken,
                    platform_token_expiry_time=datetime(1970, 1, 1, tzinfo=timezone.utc) +
                                               timedelta(milliseconds=src_dmp_context.pftokenexpiry)
                )
            )

        except xi_rest.ApiException as e:
            if e.status == 412:
                #
                _raise_interface_error(f"Could not get Insight context due to: {e.body}", e)
                #
                raise RuntimeError("_raise_interface_error will already have raised the error") from e
            raise e

    @override
    def set_insight_context(self, context: InsightContext, environment: Optional[str] = None) -> None:
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('set_insight_context'))

    @override
    def get_solution_database(self) -> SolutionDatabase:
        try:
            src_info: xi_rest.SolutionDatabase = self._api.solution_database_get()
            return SolutionDatabase(
                host=src_info.server,
                port=src_info.port if src_info.port else 3306,
                user=src_info.username,
                password=src_info.password,
                database=src_info.database
            )
        except xi_rest.ApiException as e:
            if e.status == 412:
                #
                _raise_interface_error(f"Could not get solution database info due to: {e.body}", e)
            raise e

    @override
    def set_solution_database(self, solution_database: SolutionDatabase) -> None:
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('set_solution_database'))

    @override
    def get_resource_limits(self) -> ResourceLimits:
        try:
            resource_limits: xi_rest.ResourceLimits = self._api.resource_limits_get()
            if resource_limits.memory and resource_limits.memory != 0:
                return ResourceLimits(threads=resource_limits.threads, memory=resource_limits.memory)
            return ResourceLimits(threads=resource_limits.threads)
        except xi_rest.ApiException as e:
            if e.status == 412:
                #
                _raise_interface_error(f"Could not get the job resource limits due to: {e.body}", e)
            raise e

    @override
    def set_resource_limits(self, resource_limits: ResourceLimits) -> None:
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('set_resource_limits'))

    @override
    def _populate_input_entities(self, entities: Iterable[Entity], fetch_individual_series: bool) -> None:
        entities = set(entities)
        #
        with TemporaryDirectory(prefix='.scendata_', dir=self._app.insight.work_dir) as temp_dir:
            #
            data_connector: DataConnector = self._app.app_cfg._insight_worker_data_connector_cls(
                app=self._app,
                data_container=self._app,
                scenario_path_or_id=self.scenario_id,
                parquet_dir=temp_dir,
                fetch_individual_series=fetch_individual_series,
                input_only=True,
                slow_tasks_monitor=self._slow_tasks_monitor)

            #
            data_connector.load_entities(entity_filter=lambda entity: entity in entities)

    @override
    def _set_result_entities_to_send_to_insight(self, entities: Iterable[Entity]):
        #
        self._api.entities_result_post([e.entity_name for e in entities])

    @override
    def submit_metric(self, json_doc: str) -> None:
        try:
            self._api.metrics_post(json_doc)
        except xi_rest.ApiException as e:
            if e.status == 412:
                #
                raise ValueError(f"Metric was rejected due to: {e.body}") from None
            raise e

    @override
    def get_metrics(self) -> Iterable[str]:
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('get_metrics'))

    @override
    def set_rest_client(self, client: InsightRestClient) -> None:
        raise RuntimeError(ERROR_MSG_PROD_MODE_METHOD.format('set_rest_client'))
