"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Offline interface definition.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2025 Fair Isaac Corporation. All rights reserved.
"""

import dataclasses
import datetime
import json
import os
import pickle  #
import re
import shutil
import sys
import threading
from collections import deque
from copy import copy, deepcopy
from dataclasses import dataclass, field
from typing import Dict, Generator, List, Optional, Set, Tuple, Union, Type, Any, Iterable
from xml.etree import ElementTree

from .interface_errors import (
    _raise_interface_error,
    _raise_runtime_error,
    _raise_io_error,
    ScenarioNotFoundError,
    InvalidEntitiesError,
)
from .attach_errors import (
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
    AttachType,
    ItemInfo,
    Metric,
    ObjSense,
    InsightContext,
    SolutionDatabase,
    ResourceLimits,
    SCENARIO_DATA_CONTAINER,
)
from .interface_base import AppInterfaceBase, handle_attach_errors
from ..entities import Entity
from ..entities_config import EntitiesContainer
from ..exec_mode import ExecMode
from ..repository_path import RepositoryPath
from ..scenario import InsightRestClient
from ..slow_tasks_monitor import SlowTasksMonitor
from ..type_checking import check_simple_python_type

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override


def sorted_by_key(my_dict: Dict) -> List:
    """given a dictionary returns a list of (key, value) sorted by key"""

    return [v for (_, v) in sorted(my_dict.items(), key=lambda kv: kv[0])]


ATTACH_DIR_RELATIVE_TO_INSTANCE_ROOT = ".mminsight/attach"

ATTACH_META_DATA_DIR_NAME = ".properties"
ATTACH_META_DATA_FILE_EXT = ".properties"

#
CFILE_NS = {"cf": "http://www.fico.com/xpress/optimization-modeler/model-companion"}


def write_attach_info(att: Attachment, filename: str, label: str = "attach") -> None:
    """Serializes an Attachment object to a file"""
    #
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    #
    obj = {label: att}
    with open(filename, "wb") as file:
        pickle.dump(obj, file)


def read_attach_info(filename: str, label: str = "attach") -> Attachment:
    """Deserializes an Attachment object from a file"""
    with open(filename, "rb") as file:
        obj = pickle.load(file)

    attach: Attachment = obj[label]

    return attach


@dataclass
class XpriAttachment(Attachment):
    """All meta-data about an attachment. Updated as we make local changes"""

    #
    id: str = field(default="")

    #
    is_new_attachment: bool = field(default=False)

    is_content_modified: bool = field(default=False)

    #
    local_content_filename: str = field(default="")


@dataclass
class XpriAttachmentsCache:
    """Attachments Cache"""

    #
    type: AttachType = field()  #

    #
    id: str = field(default="")

    #
    attachments: Dict[str, XpriAttachment] = field(default_factory=dict)

    #
    is_populated: bool = field(default=False)

    #
    single_file_tag_attachments: Dict[str, str] = field(default_factory=dict)


#
def read_attachment_tags_from_element(e: ElementTree.Element) -> Tuple[AttachTag, List[str]]:
    """This function converts xml.etree.ElementTree.Element to InsightAttachmentTag"""

    name = e.get("name", "")
    if name == "":
        raise ValueError("Attachment tag name cannot be empty")

    description = e.findtext("cf:description", "", CFILE_NS)

    mandatory_str = e.get("mandatory", "false")
    assert mandatory_str in ["true", "false"]
    mandatory = mandatory_str == "true"

    usage_str = e.get("usage", AttachTagUsage.MULTI_FILE.value)
    #
    if usage_str == "SINGLE_FILE":
        usage = AttachTagUsage.SINGLE_FILE
    elif usage_str == "MULTI_FILE":
        usage = AttachTagUsage.MULTI_FILE
    else:
        usage = AttachTagUsage(usage_str)

    attachments_e = e.findall("cf:attachments/cf:attachment", CFILE_NS)
    if attachments_e is None:
        attachments_e = []

    attachments = [a.text for a in attachments_e]

    return AttachTag(name, description, mandatory, usage), attachments


def read_attachment_tags_from_cfile(
        cfile_path: str,
) -> Tuple[Dict[str, AttachTag], Dict[str, List[str]]]:
    """This function reads an XML companion file and extracts all attachment tags"""

    #
    xpath = "cf:attachment-config/cf:attachment-tags/cf:attachment-tag"

    elements = ElementTree.parse(cfile_path).findall(xpath, CFILE_NS)

    attachments_by_tag = list(map(read_attachment_tags_from_element, elements))

    attach_tags = {attach_tag.name: attach_tag for (attach_tag, attachments) in attachments_by_tag}
    default_attach_tags = {
        attach_tag.name: attachments for (attach_tag, attachments) in attachments_by_tag
    }

    return attach_tags, default_attach_tags


#
# pylint: disable-next=too-many-public-methods
class AppTestInterface(AppInterfaceBase):
    """
    This class represents the Xpress Insight application interface. Use this interface to access attachments
    and metadata like the scenario ID.
    """

    #
    def __init__(
            self,
            app_id: str = "",
            app_name: str = "",
            scenario_id: str = "",
            scenario_name: str = "",
            scenario_path: str = "",
            exec_mode: str = ExecMode.NONE,  #
            test_mode: bool = True,
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

        #
        self._lock = threading.RLock()

        #
        self._msg_queue : deque[str] = deque()

        #
        if self._scenario_id == "":
            self._scenario_id = "scenid"

        if self._scenario_name == "":
            self._scenario_name = "scenname"

        if self._scenario_path == "":
            self._scenario_path = "/appname/scenname"

        if self._app_id == "":
            self._app_id = "appid"

        if self._app_name == "":
            self._app_name = "appname"

        #
        self._has_fetched_user_details: bool = False  #
        self._username: str = "UNKNOWN"
        self._user_id: str  = "UNKNOWN"

        #
        self._version: str = ''

        #

        #
        self._last_attach_id: int = 0

        #
        #
        #
        #
        self._attach_tags: Dict[
            str, AttachTag
        ] = {}  #

        #
        self._has_fetched_attach_tag_types: bool = False

        #
        #
        self._default_attach_tags: Dict[str, List[str]] = {}

        #
        self._attachment_filenames: Set[
            str
        ] = set()  #

        #
        #
        self._scen_attach_cache_map: Dict[str, XpriAttachmentsCache] = {}

        #
        self._test_mode_app_attach_dir: str = ""

        #
        self._test_mode_scen_attach_dir: str = ""

        #
        self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)

        #
        self._app_attach_cache: XpriAttachmentsCache = XpriAttachmentsCache(
            type=AttachType.APP, id=self.app_id
        )

        #
        self._attach_rules: Optional[AttachmentRules] = None
        self._has_fetched_attach_rules: bool = False

        #

        #
        #
        #
        self._item_infos_by_id: Dict[str, ItemInfo] = {}
        self._item_infos_by_path: Dict[str, ItemInfo] = {}

        #
        self._insight_context = InsightContext()

        #
        self._insight_rest_client : Optional[InsightRestClient] = None

        #
        self._solution_database = SolutionDatabase()
        self._resource_limits = ResourceLimits()
        #
        #
        self._scenario_data: Dict[str, Dict[Type, Any]] = {}

        #
        self._metrics : List[str] = []

    @override
    @property
    def work_dir(self) -> str:
        return self._work_dir

    def delete_work_dir(self):
        if os.path.isdir(self.work_dir):
            print(f'Test mode: Deleting existing Insight working directory: "{self.work_dir}".')
            shutil.rmtree(self.work_dir)

    @override
    @property
    def test_mode(self) -> bool:
        return True

    def _xpri_get_mminsight_scratch_dir(self) -> str:
        """Return path to scratch directory, creating it if necessary"""
        #
        #
        #
        #
        #
        #
        scratch_dir = os.path.join(self.work_dir, ".mminsight")
        if not os.path.isdir(scratch_dir):
            os.makedirs(scratch_dir)
        return scratch_dir

    @override
    @property
    def exec_mode(self) -> str:
        with self._exec_mode_lock:
            return self._exec_mode

    @override
    @property
    def app_id(self) -> str:
        with self._lock:
            return self._app_id

    @override
    @property
    def app_name(self) -> str:
        with self._lock:
            return self._app_name

    def _xpri_load_user_info(self):
        """Ensure that we've fetched the user details from the Insight server"""
        with self._lock:
            if not self._has_fetched_user_details:
                self._username = "Test User"
                self._user_id  = "f3c92ab3-6996-4b4b-87c9-f5a146019c51"
                self._has_fetched_user_details = True

    @override
    @property
    def username(self) -> str:
        with self._lock:
            self._xpri_load_user_info()
            return self._username

    @override
    @property
    def user_id(self) -> str:
        with self._lock:
            if not self._has_fetched_user_details:
                self._xpri_load_user_info()
            return self._user_id

    @app_id.setter
    def app_id(self, new_app_id: str):
        with self._lock:
            self._app_id = new_app_id

    @app_name.setter
    def app_name(self, new_app_name: str):
        with self._lock:
            self._app_name = new_app_name

    @username.setter
    def username(self, new_username: str):
        with self._lock:
            self._username = new_username
            self._has_fetched_user_details = True

    @user_id.setter
    def user_id(self, new_user_id: str):
        with self._lock:
            self._user_id = new_user_id

    @exec_mode.setter
    def exec_mode(self, exec_mode: str):
        with self._exec_mode_lock:
            self._exec_mode = exec_mode

    @override
    @property
    def test_cfile_path(self) -> str:
        with self._lock:
            return self._test_cfile_path

    @test_cfile_path.setter
    def test_cfile_path(self, cfile_path: str):
        with self._lock:
            self._test_cfile_path = cfile_path

    @override
    @property
    def test_attach_dir(self) -> str:
        with self._lock:
            return self._test_attach_dir

    @test_attach_dir.setter
    def test_attach_dir(self, attach_dir: str):
        with self._lock:
            self._test_attach_dir = attach_dir

    @override
    @property
    def test_app_attach_dir(self) -> str:
        with self._lock:
            return self._test_mode_app_attach_dir

    @test_app_attach_dir.setter
    def test_app_attach_dir(self, app_attach_dir: str):
        with self._lock:
            self._test_mode_app_attach_dir = app_attach_dir

    @override
    @property
    def test_scen_attach_dir(self) -> str:
        with self._lock:
            return self._test_mode_scen_attach_dir

    @test_scen_attach_dir.setter
    def test_scen_attach_dir(self, scen_attach_dir: str):
        with self._lock:
            self._test_mode_scen_attach_dir = scen_attach_dir

    @override
    @handle_attach_errors(on_error_return=None)
    def set_attach_tags(self, new_tags: List[AttachTag]):
        with self._lock:
            new_attach_tags = {t.name: t for t in new_tags}
            self._attach_tags = deepcopy(new_attach_tags)
            self._has_fetched_attach_tag_types = True

    @override
    def set_attach_rules(self, new_rules: AttachmentRules):
        with self._lock:
            self._attach_rules = deepcopy(new_rules)
            self._has_fetched_attach_rules = True

    @override
    @handle_attach_errors(on_error_return=[])
    def list_attach_tags(self) -> List[AttachTag]:
        #
        if not self._xpri_load_attach_tags():
            raise RuntimeAttachError("Failed to load attachment tags")

        #
        sorted_attach_tags = sorted_by_key(self._attach_tags)
        return sorted_attach_tags

    @override
    @handle_attach_errors(on_error_return=None)
    def get_scen_attach(self, filename: str, scenario_path: str = None, *, destination_filename: str = None) -> None:
        with self._lock:
            scenario_id = (
                self._scenario_id
                if scenario_path is None
                else self._xpri_get_scenario_id(scenario_path)
            )

            #
            #
            self._xpri_ensure_scen_attach_cache_exists(scenario_id)

            self._xpri_get_attach(self._scen_attach_cache_map[scenario_id], filename, destination_filename)

    @override
    @handle_attach_errors(on_error_return=None)
    def put_scen_attach(self, filename: str, overwrite: bool = True, *, source_filename: str = None) -> None:
        with self._lock:
            #
            #
            self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
            self._xpri_put_attach(
                self._scen_attach_cache_map[self._scenario_id], filename, source_filename, overwrite
            )

    @override
    @handle_attach_errors(on_error_return=None)
    def delete_scen_attach(self, filename: str) -> None:
        with self._lock:
            #
            #
            self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
            self._xpri_delete_attach(
                self._scen_attach_cache_map[self._scenario_id], filename
            )

    @override
    @handle_attach_errors(on_error_return=None)
    def rename_scen_attach(self, old_name: str, new_name: str) -> None:
        with self._lock:
            #
            #
            self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
            self._xpri_rename_attach(
                self._scen_attach_cache_map[self._scenario_id], old_name, new_name
            )

    @override
    @handle_attach_errors(on_error_return=None)
    def set_scen_attach_desc(self, filename: str, description: str) -> None:
        with self._lock:
            #
            #
            self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
            self._xpri_set_attach_desc(
                self._scen_attach_cache_map[self._scenario_id], filename, description
            )

    @override
    @handle_attach_errors(on_error_return=None)
    def set_scen_attach_tags(self, filename: str, tags: List[str]) -> None:
        with self._lock:
            #
            #
            self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
            self._xpri_set_attach_tags(
                self._scen_attach_cache_map[self._scenario_id], filename, tags
            )

    @override
    @handle_attach_errors(on_error_return=None)
    def set_scen_attach_hidden(self, filename: str, hidden: bool) -> None:
        with self._lock:
            #
            #
            self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
            self._xpri_set_attach_hidden(
                self._scen_attach_cache_map[self._scenario_id], filename, hidden
            )

    @override
    @handle_attach_errors(on_error_return=[])
    def list_scen_attach(self, scenario_path: str = None) -> List[Attachment]:
        with self._lock:
            scenario_id = (
                self._scenario_id
                if scenario_path is None
                else self._xpri_get_scenario_id(scenario_path)
            )

            #
            #
            self._xpri_ensure_scen_attach_cache_exists(scenario_id)
            return self._xpri_list_attach(self._scen_attach_cache_map[scenario_id])

    @override
    @handle_attach_errors(on_error_return=[])
    def list_scen_attach_by_tag(
            self, tag: str, scenario_path: str = None
    ) -> List[Attachment]:
        with self._lock:
            scenario_id = (
                self._scenario_id
                if scenario_path is None
                else self._xpri_get_scenario_id(scenario_path)
            )

            #
            #
            self._xpri_ensure_scen_attach_cache_exists(scenario_id)
            return self._xpri_list_attach_by_tag(
                self._scen_attach_cache_map[scenario_id], tag
            )

    @override
    @handle_attach_errors(on_error_return=None)
    def scen_attach_info(self, filename: str) -> Optional[Attachment]:
        with self._lock:
            #
            #
            self._xpri_ensure_scen_attach_cache_exists(self._scenario_id)
            return self._xpri_get_attach_info(
                self._scen_attach_cache_map[self._scenario_id], filename
            )

    @override
    @handle_attach_errors(on_error_return=None)
    def get_app_attach(self, filename: str, *, destination_filename: str = None) -> None:
        self._xpri_get_attach(self._app_attach_cache, filename, destination_filename)

    @override
    @handle_attach_errors(on_error_return=None)
    def list_app_attach(self) -> List[Attachment]:
        return self._xpri_list_attach(self._app_attach_cache)

    @override
    @handle_attach_errors(on_error_return=None)
    def list_app_attach_by_tag(self, tag: str) -> List[Attachment]:
        return self._xpri_list_attach_by_tag(self._app_attach_cache, tag)

    @override
    @handle_attach_errors(on_error_return=None)
    def app_attach_info(self, filename: str) -> Optional[Attachment]:
        return self._xpri_get_attach_info(self._app_attach_cache, filename)

    @override
    @handle_attach_errors(on_error_return=[])
    def get_attachs_by_tag(self, tag: str, *, destination_directory: str = None) -> Optional[List[Attachment]]:
        return self._xpri_get_attachs_by_tag(tag, destination_directory=destination_directory)

    @override
    @handle_attach_errors(on_error_return=None)
    def get_attach_by_tag(self, tag: str, *, destination_directory: str = None) -> Optional[Attachment]:
        return self._xpri_get_attach_by_tag(tag, destination_directory=destination_directory)

    @override
    @handle_attach_errors(on_error_return=[])
    def get_attach_filenames_by_tag(self, tag: str, *, destination_directory: str = None) -> List[str]:
        return self._xpri_get_attach_filenames_by_tag(tag, destination_directory=destination_directory)

    @override
    def get_attach_rules(self) -> AttachmentRules:
        with self._lock:
            self._xpri_load_attach_rules()
            return deepcopy(self._attach_rules)

    @override
    def get_item_info(self, path: str) -> ItemInfo:
        with self._lock:
            check_simple_python_type(path, 'path', str)

            #
            item_info = self._item_infos_by_id.get(path)

            if item_info is None:
                #
                parent_path = RepositoryPath(self.scenario_parent_path)
                search_path = RepositoryPath(self.scenario_path if path == '.' else path)
                norm_search_path_str = str(search_path.abspath(parent_path))
                item_info = self._item_infos_by_path.get(norm_search_path_str)

                if item_info is None:
                    _raise_interface_error(f"Item with ID '{path}' or path '{norm_search_path_str}' was not found.")

            return dataclasses.replace(item_info)

    @override
    def get_item_infos(self, folder_path: str) -> List[ItemInfo]:
        with self._lock:
            folder_item = self.get_item_info(self.scenario_parent_path if folder_path == "." else folder_path)

            if folder_item.type != 'FOLDER':
                _raise_interface_error("Item '" + folder_item.path + "' is not a folder.")

            #
            folder_item_path = folder_item.path + '/'

            return [dataclasses.replace(item)
                    for item in self._item_infos_by_id.values()
                    if item.parent_path == folder_item_path and item.id != folder_item.id]

    @override
    def add_item_info(self, item_info: ItemInfo) -> None:
        with self._lock:
            check_simple_python_type(item_info, 'item_info', ItemInfo)

            #
            item_info = dataclasses.replace(item_info)
            item_info.normalize()

            if item_info.id in self._item_infos_by_id:
                raise KeyError(f'An ItemInfo with id {repr(item_info.id)} has already been added.')

            if item_info.path in self._item_infos_by_path:
                raise KeyError(f'An ItemInfo with path {repr(item_info.path)} has already been added.')

            self._item_infos_by_id[item_info.id] = item_info
            self._item_infos_by_path[item_info.path] = item_info

    @override
    def clear_item_infos(self) -> None:
        with self._lock:
            self._item_infos_by_id: Dict[str, ItemInfo] = {}
            self._item_infos_by_path: Dict[str, ItemInfo] = {}

    def _fdelete(self, filename: str) -> bool:
        try:
            os.remove(filename)
            return False
        except Exception as e:
            _raise_io_error(f"Unable to delete attachment file {filename}.", e)

    def _xpri_get_attach_dir(self) -> str:
        """Return path to attachments work directory, creating it if necessary"""
        with self._lock:
            attach_dir = os.path.join(self._xpri_get_mminsight_scratch_dir(), "attach")
            if not os.path.isdir(attach_dir):
                os.mkdir(attach_dir)
            return attach_dir

    def _xpri_ensure_attach_dir_exists(self) -> None:
        self._xpri_get_attach_dir()

    def _xpri_get_attach_op_id(self) -> int:
        with self._lock:
            self._last_attach_id = self._last_attach_id + 1
            return self._last_attach_id

    def _xpri_load_attach_tags(self) -> bool:
        with self._lock:
            if not self._has_fetched_attach_tag_types:
                #
                if self._test_cfile_path != "":
                    (attach_tags, default_attach_tags,) = read_attachment_tags_from_cfile(
                        self._test_cfile_path
                    )
                    self._attach_tags = attach_tags
                    self._default_attach_tags = default_attach_tags

                    self._has_fetched_attach_tag_types = True
                else:
                    #
                    self._has_fetched_attach_tag_types = True

            return self._has_fetched_attach_tag_types

    def _xpri_ensure_scen_attach_cache_exists(self, scenario_id: str) -> None:
        """Ensures the scenario attachment cache for the given scenario id exists"""
        with self._lock:
            if scenario_id not in self._scen_attach_cache_map:
                #
                self._scen_attach_cache_map[scenario_id] = XpriAttachmentsCache(
                    type=AttachType.SCENARIO, id=scenario_id, is_populated=False
                )

    def _get_attach_file_path(self, attach_cache: XpriAttachmentsCache, attach_name: str) -> str:
        """ Return the local filename of a named attachment in a given attachment cache. """
        attach_root = self._xpri_get_test_mode_dir(attach_cache)
        return os.path.join(attach_root, attach_name)

    def _get_attach_properties_path(self, attach_cache: XpriAttachmentsCache, attach_name: str) -> str:
        """ Return the local filename of the properties file for the named attachment in a given attachment cache. """
        attach_root = self._xpri_get_test_mode_dir(attach_cache)
        return os.path.join(attach_root, ATTACH_META_DATA_DIR_NAME, f"{attach_name}{ATTACH_META_DATA_FILE_EXT}")

    def _xpri_get_test_mode_dir(self, attach_cache: XpriAttachmentsCache):
        """
        Return the directory to use to store simulated attachments when in test mode, creating it if it does not exist
        """
        with self._lock:
            root_dir = self._test_attach_dir
            if root_dir == "":
                root_dir = os.path.join(self._work_dir, self._test_attach_dir)
            if attach_cache.type == AttachType.APP:
                #
                if self._test_mode_app_attach_dir == "":
                    test_mode_dir = os.path.join(root_dir, "appattach")
                else:
                    test_mode_dir = self._test_mode_app_attach_dir
            elif attach_cache.type == AttachType.SCENARIO:
                if attach_cache.id != self._scenario_id:
                    raise NotImplementedError(
                        "Insight test mode currently only supports accessing attachments of current scenario & app."
                    )
                if self._test_mode_scen_attach_dir == "":
                    test_mode_dir = os.path.join(root_dir, "scenattach")
                else:
                    test_mode_dir = self._test_mode_scen_attach_dir
            else:
                raise RuntimeError(f"Unrecognized attachment cache type: {attach_cache.type}.")

            #
            if not os.path.isdir(test_mode_dir):
                os.makedirs(test_mode_dir)

            return test_mode_dir

    def _xpri_load_attach_rules(self):
        with self._lock:
            if not self._has_fetched_attach_rules:
                #
                self._attach_rules = AttachmentRules(
                    max_size=300 * 1024 * 1024,
                    max_attach_count=250,
                    max_filename_len=255,
                    invalid_filename_chars=list(r'\/?*:|"<>'),
                    max_description_len=2500,
                )

    def _xpri_get_test_mode_attachments(
            self, attach_cache: XpriAttachmentsCache
    ) -> Dict[str, XpriAttachment]:
        with self._lock:
            #
            #
            #
            #
            #

            base = self._xpri_get_test_mode_dir(attach_cache)
            attachments: Dict[str, XpriAttachment] = {}

            for root, _, files in os.walk(base):
                for file in files:
                    abs_filename = os.path.join(root, file)
                    filename = os.path.relpath(abs_filename, base)

                    if not filename.startswith(ATTACH_META_DATA_DIR_NAME + os.path.sep):
                        #
                        props_filename = self._get_attach_properties_path(attach_cache, filename)

                        #
                        if os.path.isfile(props_filename):
                            attach: Attachment = read_attach_info(props_filename)

                            #
                            if attach.filename == "" or attach.filename is None:
                                attach.filename = filename

                        else:

                            attach: Attachment = Attachment(
                                filename=filename,
                                description="",
                                tags=[],
                                size=os.path.getsize(abs_filename),
                                last_modified_user="Test User",
                                last_modified_date=datetime.datetime.fromtimestamp(
                                    os.path.getmtime(abs_filename)
                                ),
                                hidden=False,
                            )

                            #
                            if attach_cache.type == AttachType.APP:
                                #
                                #
                                if not self._xpri_load_attach_tags():
                                    raise RuntimeAttachError("Unable to load attach tags.")

                                for (tag, filenames) in self._default_attach_tags.items():
                                    if filename in filenames and tag not in attach.tags:
                                        attach.tags.append(tag)

                            #
                            write_attach_info(attach, props_filename)

                        #
                        xpri_attach: XpriAttachment = XpriAttachment(
                            filename=attach.filename,
                            description=attach.description,
                            tags=attach.tags,
                            size=attach.size,
                            last_modified_user=attach.last_modified_user,
                            last_modified_date=attach.last_modified_date,
                            hidden=attach.hidden,
                            local_content_filename=filename,
                        )

                        if file in attachments:
                            _raise_runtime_error(
                                f"Multiple attachments on same item have filename: {xpri_attach.filename}."
                            )
                        else:
                            attachments[xpri_attach.filename] = xpri_attach

            return attachments

    def _xpri_find_test_mode_attachment(
            self, attach_cache: XpriAttachmentsCache, attach_name: str
    ) -> XpriAttachment:

        attachments = self._xpri_get_test_mode_attachments(attach_cache)

        return attachments.get(attach_name, None)

    def _xpri_attach_exists(
            self, attach_cache: XpriAttachmentsCache, filename: str
    ) -> bool:
        #

        assert attach_cache.is_populated

        return self._xpri_find_test_mode_attachment(attach_cache, filename) is not None

    def _xpri_save_test_mode_attachment_properties(
            self, attach_cache: XpriAttachmentsCache, new_props: XpriAttachment
    ) -> None:
        """Save the attachment properties of a given attachment"""
        with self._lock:
            attach = new_props  #

            props_filename = self._get_attach_properties_path(attach_cache, new_props.local_content_filename)
            write_attach_info(attach, props_filename, "attach")

    def _xpri_populate_cache(self, attach_cache: XpriAttachmentsCache) -> bool:
        with self._lock:
            if attach_cache.is_populated:
                return True

            #
            attach_cache.is_populated = True
            return True

    def _xpri_check_can_add_new_attach(
            self, attach_cache: XpriAttachmentsCache
    ) -> bool:
        #
        with self._lock:
            if attach_cache.type != AttachType.SCENARIO:
                raise NotImplementedError(
                    f"Attachment rules for attachment type '{attach_cache.type}' not implemented."
                )

            self._xpri_load_attach_rules()
            assert self._attach_rules is not None
            test_attachments = self._xpri_get_test_mode_attachments(attach_cache)
            return len(test_attachments) < self._attach_rules.max_attach_count

    def _xpri_check_attach_filename(
            self, attach_cache: XpriAttachmentsCache, filename: str
    ) -> bool:
        """Check whether an attachment's filename is valid"""
        with self._lock:
            del attach_cache  #

            self._xpri_load_attach_rules()
            assert self._attach_rules is not None
            if filename == "" or len(filename) > self._attach_rules.max_filename_len:
                return False

            for c in self._attach_rules.invalid_filename_chars:
                if c in filename:
                    return False

            return True

    def _xpri_check_attach_file_size(
            self, attach_cache: XpriAttachmentsCache, filename: str
    ) -> bool:
        #
        with self._lock:
            del attach_cache  #

            self._xpri_load_attach_rules()
            assert self._attach_rules is not None
            return os.path.getsize(filename) <= self._attach_rules.max_size

    def _xpri_check_attach_description(
            self, attach_cache: XpriAttachmentsCache, description: str
    ) -> bool:
        """Check whether an attachment's description is valid"""
        with self._lock:
            del attach_cache  #

            self._xpri_load_attach_rules()
            assert self._attach_rules is not None
            return len(description) <= self._attach_rules.max_description_len

    def _xpri_check_tags_valid(self, tags: List[str]) -> bool:
        #
        if not self._xpri_load_attach_tags():
            return False  #

        for tag in tags:
            if tag not in self._attach_tags:
                return False

        return True

    def _xpri_get_attach_common(
            self, attach_cache: XpriAttachmentsCache, filename: str, destination_filename: str = None
    ) -> None:
        #
        with self._lock:
            #
            if not self._xpri_populate_cache(attach_cache):
                raise RuntimeAttachError('Failed to load attachments cache')

            #
            test_attach = self._xpri_find_test_mode_attachment(attach_cache, filename)
            if test_attach is None:
                raise AttachNotFoundError(f'Attachment "{filename}" not found')

            src = os.path.join(
                self._xpri_get_test_mode_dir(attach_cache),
                test_attach.local_content_filename,
            )
            try:
                shutil.copy(src, filename if (destination_filename is None) else destination_filename)
            except Exception as e:
                _raise_io_error(f"Unable to write or overwrite file {filename}.", e)
                #

    def _xpri_get_attach(
            self, attach_cache: XpriAttachmentsCache, filename: str, destination_filename: str = None
    ) -> None:
        self._xpri_get_attach_common(attach_cache, filename, destination_filename)

    def _xpri_put_attach(
            self, attach_cache: XpriAttachmentsCache, filename: str, source_filename: Optional[str], overwrite: bool
    ) -> None:
        #
        with self._lock:
            if source_filename is None:
                source_filename = filename

            #
            if not self._xpri_populate_cache(attach_cache):
                raise RuntimeAttachError('Failed to load attachments cache')

            #
            if not overwrite and self._xpri_attach_exists(attach_cache, filename):
                raise AttachAlreadyExistsError('Attachment already exists')

            if not self._xpri_check_attach_filename(attach_cache, filename):
                raise AttachFilenameInvalidError('Attachment filename invalid')

            if not self._xpri_check_can_add_new_attach(
                    attach_cache
            ) and not self._xpri_attach_exists(attach_cache, filename):
                raise TooManyAttachError('Scenario has too many attachments')

            #
            if not os.path.isfile(source_filename):
                _raise_io_error(f"Attachment file '{source_filename}' not found.")

            if not self._xpri_check_attach_file_size(attach_cache, source_filename):
                raise AttachTooLargeError('Attachment exceeds maximum permitted size')

            #
            test_attach: XpriAttachment = self._xpri_find_test_mode_attachment(
                attach_cache, filename
            )
            if test_attach is None:
                #
                test_attach = XpriAttachment(
                    filename=filename,
                    description="",
                    tags=[],
                    hidden=False,
                    local_content_filename=filename,
                )

                c = 1
                while os.path.isfile(
                        self._get_attach_file_path(attach_cache, test_attach.local_content_filename)
                ):
                    c = c + 1
                    test_attach.local_content_filename = f"{filename}_{c}"

            #
            test_attach.size = os.path.getsize(source_filename)
            test_attach.last_modified_user = self.username
            test_attach.last_modified_date = datetime.datetime.now()

            #
            test_attach_path = os.path.join(
                self._xpri_get_test_mode_dir(attach_cache),
                test_attach.local_content_filename,
            )

            try:
                os.makedirs(os.path.dirname(test_attach_path), exist_ok=True)
            except Exception as e:
                _raise_io_error(f"Unable to create parent directory for file {test_attach_path}.", e)
                #

            try:
                shutil.copy(source_filename, test_attach_path)
            except Exception as e:
                _raise_io_error(f"Unable to copy attachment from {filename} to {test_attach_path}.", e)
                #

            #
            self._xpri_save_test_mode_attachment_properties(attach_cache, test_attach)

    def _xpri_delete_attach(
            self, attach_cache: XpriAttachmentsCache, filename: str
    ) -> None:
        #
        with self._lock:
            #
            if not self._xpri_populate_cache(attach_cache):
                raise RuntimeAttachError('Failed to populate attachment cache')

            #
            if not self._xpri_attach_exists(attach_cache, filename):
                raise AttachNotFoundError(f'Attachment "{filename}" was not found')

            att: XpriAttachment = self._xpri_find_test_mode_attachment(
                attach_cache, filename
            )
            if att is None:
                _raise_runtime_error("Attachment should exist if we reach this point.")

            att_path = os.path.join(
                self._xpri_get_test_mode_dir(attach_cache), att.local_content_filename
            )

            try:
                os.remove(att_path)
            except Exception as e:
                _raise_io_error(f"Unable to delete attachment file {att_path}.", e)
                #

            prop_file = self._get_attach_properties_path(attach_cache, att.local_content_filename)
            if os.path.isfile(prop_file):
                try:
                    os.remove(prop_file)
                except Exception as e:
                    _raise_io_error(f"Unable to delete attachment file {prop_file}.", e)
                    #

    #
    def _xpri_rename_attach(
            self, attach_cache: XpriAttachmentsCache, old_name: str, new_name: str
    ) -> None:
        with self._lock:
            #
            if not self._xpri_populate_cache(attach_cache):
                raise RuntimeAttachError('Failed to populate attachment cache')

            #
            if old_name == new_name:
                #
                return

            if not self._xpri_attach_exists(attach_cache, old_name):
                raise AttachNotFoundError(f'Attachment "{old_name}" was not found')
            if self._xpri_attach_exists(attach_cache, new_name):
                raise AttachAlreadyExistsError('Attachment of this name already exists')
            if not self._xpri_check_attach_filename(attach_cache, new_name):
                raise AttachFilenameInvalidError('Invalid attachment filename')

            #
            test_attach = self._xpri_find_test_mode_attachment(attach_cache, old_name)
            if test_attach is None:
                _raise_runtime_error("Attachment should exist if we reach this point.")

            test_attach.filename = new_name
            self._xpri_save_test_mode_attachment_properties(attach_cache, test_attach)

    #
    def _xpri_set_attach_desc(
            self, attach_cache: XpriAttachmentsCache, filename: str, description: str
    ):
        with self._lock:
            #
            if not self._xpri_populate_cache(attach_cache):
                raise RuntimeAttachError('Failed to populate attachment cache')

            #
            if not self._xpri_attach_exists(attach_cache, filename):
                raise AttachNotFoundError(f'Attachment "{filename}" not found')

            if not self._xpri_check_attach_description(attach_cache, description):
                raise AttachDescriptionInvalidError('Invalid attachment description')

            #
            test_attach = self._xpri_find_test_mode_attachment(attach_cache, filename)
            if test_attach is None:
                _raise_runtime_error("Attachment should exist if we reach this point.")

            test_attach.description = description
            self._xpri_save_test_mode_attachment_properties(attach_cache, test_attach)

    #
    def _xpri_set_attach_tags(
            self, attach_cache: XpriAttachmentsCache, filename: str, new_tags: List[str]
    ):
        with self._lock:
            #
            if not self._xpri_populate_cache(attach_cache):
                raise RuntimeAttachError('Failed to populate attachment cache')

            #
            if not self._xpri_attach_exists(attach_cache, filename):
                raise AttachNotFoundError(f'Attachment "{filename}" not found')

            #
            if not self._xpri_check_tags_valid(new_tags):
                raise AttachTagsInvalidError('Invalid attachment tags')

            #
            test_attach = self._xpri_find_test_mode_attachment(attach_cache, filename)
            if test_attach is None:
                _raise_runtime_error("Attachment should exist if we reach this point.")

            test_attach.tags = list(set(new_tags))  #
            self._xpri_save_test_mode_attachment_properties(attach_cache, test_attach)

            #
            all_test_attach = None
            for tag in new_tags:
                if self._attach_tags[tag].usage == AttachTagUsage.SINGLE_FILE:
                    if all_test_attach is None:
                        all_test_attach = self._xpri_get_test_mode_attachments(
                            attach_cache
                        )

                    for (test_attach_filename, attachment) in all_test_attach.items():
                        if test_attach_filename != filename and tag in attachment.tags:
                            attachment.tags.remove(tag)
                            self._xpri_save_test_mode_attachment_properties(
                                attach_cache, attachment
                            )

    #
    def _xpri_set_attach_hidden(
            self, attach_cache: XpriAttachmentsCache, filename: str, hidden: bool
    ) -> None:
        with self._lock:
            #
            if not self._xpri_populate_cache(attach_cache):
                raise RuntimeAttachError('Failed to populate attachment cache')

            #
            if not self._xpri_attach_exists(attach_cache, filename):
                raise AttachNotFoundError(f'Attachment "{filename}" does not exist')

            #
            test_attach = self._xpri_find_test_mode_attachment(attach_cache, filename)
            if test_attach is None:
                _raise_runtime_error("Attachment should exist if we reach this point.")
            test_attach.hidden = hidden
            self._xpri_save_test_mode_attachment_properties(attach_cache, test_attach)

    def _xpri_list_attach_common(
            self, attach_cache: XpriAttachmentsCache
    ) -> Optional[List[Attachment]]:
        with self._lock:
            #
            #

            #
            if not self._xpri_populate_cache(attach_cache):
                raise RuntimeAttachError('Failed to populate attachment cache')

            test_attachments = self._xpri_get_test_mode_attachments(attach_cache)
            sorted_test_attachments = sorted_by_key(test_attachments)
            return sorted_test_attachments

    def _xpri_list_attach(self, attach_cache: XpriAttachmentsCache) -> List[Attachment]:
        #
        return self._xpri_list_attach_common(attach_cache)

    #
    def _xpri_list_attach_by_tag_common(
            self, attach_cache: XpriAttachmentsCache, tag: str
    ) -> Optional[List[Attachment]]:
        all_attachments = self._xpri_list_attach_common(attach_cache)
        return [attach for attach in all_attachments if tag in attach.tags]

    #
    def _xpri_list_attach_by_tag(
            self, attach_cache: XpriAttachmentsCache, tag: str
    ) -> List[Attachment]:
        with self._lock:
            if not self._xpri_check_tags_valid([tag]):
                raise AttachTagsInvalidError('Attachment tags are invalid')

            return self._xpri_list_attach_by_tag_common(attach_cache, tag)

    #
    def _xpri_get_attach_info(
            self, attach_cache: XpriAttachmentsCache, filename: str
    ) -> Optional[Attachment]:
        with self._lock:
            #
            if not self._xpri_populate_cache(attach_cache):
                raise RuntimeAttachError('Failed to populate attachment cache')
            if not self._xpri_attach_exists(attach_cache, filename):
                raise AttachNotFoundError(f'Attachment "{filename}" was not found')

            test_attach = self._xpri_find_test_mode_attachment(attach_cache, filename)
            if test_attach is None:
                _raise_runtime_error("Attachment should exist if we reach this point.")
            attach = deepcopy(test_attach)
            return attach

    #
    def _xpri_get_scenario_id(self, scenario_path: str) -> str:
        if scenario_path == self._scenario_path:
            return self._scenario_id

        raise NotImplementedError("Access to other scenarios is currently not supported in Insight test mode.")

    #
    def _xpri_get_attachs_by_tag(self, tag: str, destination_directory: str = None) -> Optional[List[Attachment]]:
        with self._lock:
            if not destination_directory:
                destination_directory = '.'

            #
            if not self._xpri_check_tags_valid([tag]):
                raise AttachTagsInvalidError('Attachment tags were invalid')

            #
            attach_cache = self._scen_attach_cache_map[self._scenario_id]
            atts = self._xpri_list_attach_by_tag_common(attach_cache, tag)

            #
            if not atts:
                attach_cache = self._app_attach_cache
                atts = self._xpri_list_attach_by_tag_common(attach_cache, tag)

            #
            if not atts:
                raise AttachNotFoundError(f'Attachment with tag "{tag}" was not found')

            #
            for attach in atts:
                dest_path = os.path.join(destination_directory, attach.filename)
                self._xpri_get_attach_common(attach_cache, attach.filename, dest_path)

            return atts

    #
    def _xpri_get_attach_filenames_by_tag(self, tag: str, destination_directory: str = None) -> List[str]:
        with self._lock:
            attachments = self._xpri_get_attachs_by_tag(tag, destination_directory)
            return [attach.filename for attach in attachments]

    #
    def _xpri_get_attach_by_tag(self, tag: str, destination_directory: str = None) -> Optional[Attachment]:
        with self._lock:
            if not destination_directory:
                destination_directory = '.'

            if not self._xpri_check_tags_valid([tag]):
                raise AttachTagsInvalidError('Invalid attachment tags')

            atts = self._xpri_list_attach_by_tag_common(
                self._scen_attach_cache_map[self._scenario_id], tag
            )

            assert atts is not None
            if len(atts) > 1:
                raise SeveralAttachFoundError('Found multiple matching attachments')

            if len(atts) == 1:
                attachment = atts[0]
                self._xpri_get_attach_common(
                    self._scen_attach_cache_map[self._scenario_id],
                    attachment.filename,
                    os.path.join(destination_directory, attachment.filename)
                )
                return attachment

            atts = self._xpri_list_attach_by_tag_common(
                self._app_attach_cache, tag
            )

            assert atts is not None
            if len(atts) == 0:
                raise AttachNotFoundError('Found no matching attachments')
            if len(atts) > 1:
                raise SeveralAttachFoundError('Found multiple matching attachments')

            assert len(atts) == 1
            attachment = atts[0]
            self._xpri_get_attach_common(
                self._app_attach_cache, attachment.filename,
                os.path.join(destination_directory, attachment.filename)
            )
            return attachment

    #

    #

    @override
    @property
    def scenario_id(self):
        with self._lock:
            return self._scenario_id

    @scenario_id.setter
    def scenario_id(self, scenario_id: str):
        with self._lock:
            self._scenario_id = scenario_id

    @override
    @property
    def scenario_name(self) -> str:
        with self._lock:
            return self._scenario_name

    @scenario_name.setter
    def scenario_name(self, scenario_name: str):
        with self._lock:
            self._scenario_name = scenario_name

    @override
    @property
    def scenario_path(self) -> str:
        with self._lock:
            return self._scenario_path

    @scenario_path.setter
    def scenario_path(self, scenario_path: str):
        path = RepositoryPath(scenario_path)

        if not path.is_absolute:
            raise ValueError("The scenario path must be absolute.")

        #
        path = path.abspath(current_dir=RepositoryPath('/'))

        if len(path.elements) <= 1:
            raise ValueError("The normalized scenario path must have more than one elements. "
                             "Example: '/appname/scenname'")

        with self._lock:
            self._scenario_path = str(path)

    @override
    def get_scenario_data(self, scenario_path_or_id: str, scenario_data_class: Type[SCENARIO_DATA_CONTAINER], *,
                          fetch_individual_series=False) -> SCENARIO_DATA_CONTAINER:
        with self._lock:
            if not issubclass(scenario_data_class, EntitiesContainer):
                raise TypeError("Scenario data class must be decorated with @xi.ScenarioData.")

            if scenario_path_or_id not in self._scenario_data:
                raise ScenarioNotFoundError(f"No scenario data for scenario '{scenario_path_or_id}'.")

            if scenario_data_class not in self._scenario_data[scenario_path_or_id]:
                raise InvalidEntitiesError(f"No scenario data of type {scenario_data_class.__name__} for "
                                           f"scenario '{scenario_path_or_id}'.")

            #
            #
            return deepcopy(self._scenario_data[scenario_path_or_id][scenario_data_class])

    @override
    def set_scenario_test_data(self, scenario_path_or_id: str, scenario_data_class: Type[SCENARIO_DATA_CONTAINER],
                               scenario_data: SCENARIO_DATA_CONTAINER):
        with self._lock:
            if not issubclass(scenario_data_class, EntitiesContainer):
                raise TypeError("Scenario data class must be decorated with @xi.ScenarioData.")

            if scenario_path_or_id not in self._scenario_data:
                self._scenario_data[scenario_path_or_id] = {}

            self._scenario_data[scenario_path_or_id][scenario_data_class] = scenario_data

    @override
    def update(self, metric: Metric, value: Union[float, int, ObjSense]) -> None:
        pass

    @override
    def reset_progress(self) -> None:
        pass

    @override
    def send_progress_update(self) -> None:
        exec_mode = self._app.app_cfg.get_exec_mode(self.exec_mode)

        #
        if exec_mode is not None and exec_mode.send_progress:
            #
            self._app.data_connector.save_progress()

    @override
    def get_messages(self) -> Generator[str, None, None]:
        # pylint: disable=consider-using-with
        self._lock.acquire()
        while self._msg_queue:
            self._lock.release()
            yield self._msg_queue.popleft()
            self._lock.acquire()
        self._lock.release()

    @override
    def put_messages(self, *msgs: str) -> None:
        for msg in msgs:
            #
            #
            #
            if msg is None or not isinstance(msg, str):
                raise ValueError("A progress message must be a string.")

            #
            #
            #
            if len(msg) == 0:
                raise ValueError("A progress message must not be an empty string.")

            #
            #
            if not re.match('^[^\x00-\x1F\x7F]*$',msg):
                raise ValueError("A progress message must not contain any control characters.")

        #
        with self._lock:
            self._msg_queue.extend(msgs)

    @override
    @property
    def version(self) -> str:
        with self._lock:
            return self._version

    @version.setter
    def version(self, new_version: str):
        with self._lock:
            self._version = new_version

    @override
    def get_insight_context(self, environment : Optional[str] = None) -> InsightContext:
        with self._lock:
            return self._insight_context

    @override
    def set_insight_context(self, context: InsightContext) -> None:
        with self._lock:
            self._insight_context = context

    @override
    def get_solution_database(self) -> SolutionDatabase:
        with self._lock:
            return self._solution_database

    @override
    def set_solution_database(self, solution_database: SolutionDatabase) -> None:
        with self._lock:
            self._solution_database = solution_database

    @override
    def get_resource_limits(self) -> ResourceLimits:
        with self._lock:
            return self._resource_limits

    @override
    def set_resource_limits(self, resource_limits: ResourceLimits) -> None:
        with self._lock:
            self._resource_limits = resource_limits

    @override
    def _populate_input_entities(self, entities: Iterable[Entity], fetch_individual_series: bool) -> None:
        #
        self._app.data_connector.load_partial_input(entities)

    @override
    def _set_result_entities_to_send_to_insight(self, entities: Iterable[Entity]):
        #
        pass

    @override
    def submit_metric(self, json_doc: str) -> None:
        #
        try:
            json.loads(json_doc)
        except ValueError as e:
            raise ValueError("Metric rejected as it is not valid JSON") from e

        #
        self._metrics.append(json_doc)

    @override
    def get_metrics(self) -> Iterable[str]:
        return copy(self._metrics)

    @override
    def get_rest_client(self, *,
                        client_id: Optional[str] = None,
                        secret: Optional[str] = None,
                        max_retries: int = 5) -> InsightRestClient:
        #
        if self._insight_rest_client:
            return self._insight_rest_client

        #
        if self._insight_context.insight_url:
            return super().get_rest_client(client_id=client_id, secret=secret, max_retries=max_retries)

        #
        raise RuntimeError('In test mode, REST client is only available if "set_rest_client" has been called, '
                           'or "set_insight_context" has been passed a context with a valid Insight URL.')

    @override
    def set_rest_client(self, client: InsightRestClient) -> None:
        self._insight_rest_client = client
