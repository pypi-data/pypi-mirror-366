"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Interface base class.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2025 Fair Isaac Corporation. All rights reserved.
"""

import datetime
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Generator, Optional, Union, Type, TypeVar, Iterable, Callable
from warnings import warn

from ..entities import EntityBase, Entity
from ..exec_mode import ExecMode
from ..repository_path import RepositoryPath
from ..slow_tasks_monitor import SlowTasksMonitor
from ..type_checking import check_instance_attribute_types, XiEnum
from .. import scenario as ins
from .attach_errors import AttachStatus

#


#
#
#
#
SCENARIO_DATA_CONTAINER = TypeVar('SCENARIO_DATA_CONTAINER')


class Metric(XiEnum):
    """
    Indicates the type of metric a progress update is providing.

    Attributes
    ----------
    GAP : float
        The gap to the optimal solution, as a percentage.
    OBJVAL : float
        The best solution value found so far.
    NUMSOLS : float
        The count of feasible solutions found so far.
    OBJSENSE : ObjSense
        The direction of the solve.

    See Also
    --------
    AppInterface.update
    AppInterface.reset_progress

    Notes
    -----
    This enumeration is used in the Insight 4 progress updates methods.
    """

    GAP = 1
    OBJVAL = 2
    NUMSOLS = 3
    OBJSENSE = 4


class ObjSense(XiEnum):
    """
    Indicates the direction of optimization.

    Attributes
    ----------
    MINIMIZE : int
        This is a minimization problem.
    MAXIMIZE : int
        This is a maximization problem.

    See Also
    --------
    AppInterface.update
    AppInterface.reset_progress

    Notes
    -----
    This enumeration is used in the Insight 4 progress updates methods.
    """

    MINIMIZE = 1
    MAXIMIZE = -1


#
class AttachType(XiEnum):
    """
    Possible values for attachment type
    """

    APP = "APP"
    SCENARIO = "SCENARIO"


class AttachTagUsage(XiEnum):
    """
    Possible values for attachment tag usage.

    Attributes
    ----------
    SINGLE_FILE : str
        This tag may only be assigned to at most one attachment file.
    MULTI_FILE : str
        This tag may only be assigned to any number of attachment files.
    """

    SINGLE_FILE = "single-file"
    MULTI_FILE = "multi-file"


@dataclass  #
class AttachTag:
    """
    A class containing information about a tag defined in the app's companion file.

    Attributes
    ----------
    name : str
        Name of the tag.
    description : str
        Description of the tag.
    mandatory : bool
        Whether the tag is mandatory.
    usage : AttachTagUsage
        Tag usage restrictions, either `AttachTagUsage.SINGLE_FILE` or `AttachTagUsage.MULTI_FILE`.

    Notes
    -----
    Modifying an `AttachTag` record will not modify the attachment tag information on the server.

    See Also
    --------
    AppInterface.list_attach_tags
    """

    name: str = field(default="")
    description: str = field(default="")
    mandatory: bool = field(default=False)
    usage: AttachTagUsage = field(default=AttachTagUsage.MULTI_FILE)


@dataclass
class Attachment:
    """
    An object containing information about a single attachment.

    Attributes
    ----------
    filename : str
        Filename of the attachment
    description : str
        Description of the attachment
    tags : List[str]
        Collection of tags associated with the attachment
    size : int
        Size of the attachment, in bytes
    last_modified_user : str
        Name of the last Insight user to modify the attachment
    last_modified_date : datetime.datetime
        Date and time of last modification to attachment
    hidden : bool
        Whether the attachment is hidden from the UI
    """

    filename: str = field(default="")
    description: str = field(default="")
    tags: List[str] = field(default_factory=list)
    size: int = field(default=0)
    last_modified_user: str = field(default="")
    last_modified_date: Optional[datetime.datetime] = field(default=None)
    hidden: bool = field(default=False)


@dataclass
class AttachmentRules:
    """
    A class containing information about the rules used by Insight when verifying attachments.

    Attributes
    ----------
    max_size : int
        The maximum size, in bytes, that an attachment may have.
    max_attach_count : int
        The maximum number of attachments that can be attached to a single scenario.
    max_filename_len : int
        The maximum permitted length, in characters, of an attachment filename.
    invalid_filename_chars : List[str]
        A list of characters that are not permitted in attachment filenames.
        Must be a list of single-character string values.
    max_description_len : int
        The maximum permitted length, in characters, of an attachment description.

    Notes
    -----
    This object is used only in test mode.

    See Also
    --------
    AppInterface.set_attach_rules
    AppInterface.test_mode
    """

    max_size: int = field(default=0)
    max_attach_count: int = field(default=0)
    max_filename_len: int = field(default=0)

    #
    invalid_filename_chars: List[str] = field(default_factory=list)

    max_description_len: int = field(default=0)


@dataclass
class ItemInfo:
    """
    A class containing information for a repository item.

    Attributes
    ----------
    id : str
        Item id.
    type : str
        Item type (`"FOLDER"` or scenario type identifier). Default: 'SCENARIO'.
    name : str
        Item name.
    path : str
        Item path. Equivalent to `parent_path + RepositoryPath.encode_element(name)`,
        except for application root folders.
    parent_path : str
        Item parent path. Begins and ends with a slash '/'.

    Examples
    --------
    Create an ItemInfo for use in a test.

    >>> insight.add_item_info(xi.ItemInfo(
    ...             id='my_scenario_id',
    ...             name='My Scenario Name',
    ...             type='SCENARIO',
    ...             path='/my_app/my_folder/my_scenario',
    ...             parent_path='/my_app/my_folder'))


    See Also
    --------
    AppInterface.get_item_info
    AppInterface.get_item_infos
    AppInterface.add_item_info
    AppInterface.clear_item_infos
    RepositoryPath
    """

    id: str = field()
    type: str = field(default="SCENARIO")
    name: str = field(default="")
    path: str = field(default="")
    parent_path: str = field(default="")

    def normalize(self):
        """ Validate the attribute values of the ItemInfo and normalize the path attributes. """
        check_instance_attribute_types(self)

        if self.id == '':
            #
            #
            raise ValueError("The ItemInfo id must not be the empty string.")

        if self.name in ['', '.', '..']:
            raise ValueError('The ItemInfo name cannot be equal to "", ".", or "..".')

        #
        for path_name in ['path', 'parent_path']:
            if not self.__dict__[path_name].startswith("/"):
                raise ValueError(f'The ItemInfo {path_name} must be absolute (start with "/"), '
                                 f'but it is: {self.__dict__[path_name]}')

        #
        norm_root = RepositoryPath('/')  #
        norm_path = RepositoryPath(self.path).abspath(norm_root)
        norm_parent_path = RepositoryPath(self.parent_path).abspath(norm_path)
        norm_path_len = len(norm_path.elements)
        norm_path_str = str(norm_path)
        norm_parent_path_str = str(norm_parent_path)

        if norm_path_len == 0:
            raise ValueError(f'The normalized ItemInfo path cannot be empty, but it is '
                             f'(before normalization): {self.path}')

        if norm_path_len == 1:
            #
            if self.name != 'Root':
                raise ValueError(f'The ItemInfo name of the application root folder must '
                                 f"be 'Root', but it is '{self.name}'. Folder path: {norm_path_str}")

            if self.type != 'FOLDER':
                raise ValueError(f'The ItemInfo type of the application root folder must '
                                 f"be 'FOLDER', but it is '{self.type}'. Folder path: {norm_path_str}")

            if norm_parent_path_str != norm_path_str:
                raise ValueError(f'The ItemInfo parent_path of the application root folder must '
                                 f"be equal to its path '{norm_path_str}', but it is: {self.parent_path}")
        else:
            #
            norm_parent_path.append(self.name)
            norm_path_str_expected = str(norm_parent_path)

            if norm_path_str != norm_path_str_expected:
                raise ValueError(f"The ItemInfo path must be '{norm_path_str_expected}', but it is: {norm_path_str}")

        self.path = norm_path_str
        self.parent_path = norm_parent_path_str + '/'  #


@dataclass
#
# pylint: disable-next=too-many-instance-attributes
class InsightDmpContext:
    """
    An object containing information about the app's execution context within DMP.

    Attributes
    ----------
    manager_url : str
        The URL of DMP Manager, which can be used to call DMP Manager webservice endpoints.
    environment : str
        The lifecycle environment of the component instance executing the Insight app, e.g. "design".
    tenant_id : str
        The ID of the tenant in which the Insight component resides.
    solution_id : str
        The ID of the solution in which the Insight component resides.
    component_id : str
        The ID of the Insight component that is executing the app.
    component_instance_id : str
        The ID of the Insight component instance that is executing the app.
    solution_token : str
        A bearer token that can be used to authorize requests to this component, DMP manager and other DMP resources,
        with the authority of the solution user for the requested environment.
    solution_token_expiry_time : datetime.datetime
        The expiry time of the given solution token.
    solution_token_environment : str
        The lifecycle environment for which the solution token was authorized, e.g. "design".
    platform_token : str
        A bearer token that can be used to authorize requests for the platform resources, under the authority of
        the platform client id.
    platform_token_expiry_time : datetime.datetime
        The expiry time of the given platform token.
    """

    manager_url: str = field(default="")
    environment: str = field(default="")
    tenant_id: str = field(default="")
    solution_id: str = field(default="")
    component_id: str = field(default="")
    component_instance_id: str = field(default="")
    solution_token: str = field(default="")
    solution_token_expiry_time: datetime.datetime = field(default=datetime.datetime(1970, 1, 1))
    solution_token_environment: str = field(default="")
    platform_token: str = field(default="")
    platform_token_expiry_time: datetime.datetime = field(default=datetime.datetime(1970, 1, 1))


@dataclass
class InsightContext:
    """
    An object containing information about the context in which the Insight app is executing.

    Attributes
    ----------
    insight_url : str
        The URL of the Insight component executing the app.
    trace_id : str
        The B3 Propagation TraceId value; every span in a trace shares this ID.
    span_id : str
        The B3 Propagation SpanId value.
    parent_span_id : str
        The B3 Propagation ParentSpanId value, or 'None' if not present.
    sampled : str
        The B3 Propagation Sampled value; either `1`, `0`, or 'None' if not present.
    dmp : Optional[InsightDmpContext]
        Information about the DMP solution that is executing the app, when the app is executing in DMP, or 'None'
        when executing outside DMP.
    """

    insight_url: str = field(default="")
    trace_id: str = field(default="")
    span_id: str = field(default="")
    parent_span_id: Optional[str] = field(default=None)
    sampled: Optional[str] = field(default=None)
    dmp: Optional[InsightDmpContext] = field(default=None)


@dataclass
class SolutionDatabase:
    """
    An object containing information about the shared MySQL solution database of the current DMP solution.

    Attributes
    ----------
    host : str
        The hostname of the solution database server.
    port : int
        The port on which to connect to the solution database server.
    user : str
        The username to use for accessing to the solution database.
    password : str
        The password to use for accessing to the solution database.
    database : str
        The name of the solution database.
    """

    host: str = field(default="")
    port: int = field(default=3306)
    user: str = field(default="")
    password: str = field(default="")
    database: str = field(default="")


@dataclass
class ResourceLimits:
    """
    An object containing information about the thread and memory limits during scenario execution.

    Attributes
    ----------
    memory : Optional[int]
        The amount of memory in megabytes available for use during scenario execution.
    threads : int
        The number of threads available for use during scenario execution.
    """
    memory: Optional[int] = None
    threads: int = field(default=1)


#
# pylint: disable-next=too-many-public-methods
class AppInterface(ABC):
    """
    This class represents the Xpress Insight application interface. Use this interface to access attachments
    and metadata like the scenario ID.

    See Also
    --------
    AppBase.insight
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
            force_wdir_to_temp: Optional[bool] = None,  #
            tmp_dir: Optional[str] = None,   #
            work_dir: str = os.path.join("work_dir", "insight"),
            app=None,
            slow_tasks_monitor: Optional[SlowTasksMonitor] = None
    ) -> None:
        """
        Constructor of the Insight application interface.

        Parameters
        ----------
        app_id : str
            The globally unique identifier string for the application in the Xpress-Insight repository.
        app_name : str
            The name of the application in the Xpress-Insight repository.
        scenario_id : str
            The globally unique identifier string for the scenario in the Xpress-Insight repository.
        scenario_name : str
            The name of the scenario in the Xpress-Insight repository.
        scenario_path : str
            The repository path of the current scenario in the Xpress-Insight repository.
        exec_mode : str
            The Execution Mode to apply to the current scenario in the Xpress-Insight repository.
        test_mode : bool
            Whether the `xpressinsight` package is running in test mode.
        test_attach_dir : str
            Location to store mock attachments for app and scenario, when in test mode.
        test_cfile_path : str
            Location of the app companion file to parse, when in test mode.
        work_dir : str
            Internal working directory of the `xpressinsight` package.
        app : AppBase
            The Insight Python application which this interface will serve.
        slow_tasks_monitor : SlowTasksMonitor
            Object that will be used to track and report on 'slow' tasks
        raise_attach_exceptions : bool, optional
            Whether errors during attachment operations should be raised as exceptions (`True`). If `False` or
            unset, the app developer must check the `attach_status` property of `AppInterface` after every attachment
            operation to check if it succeeded.
        """
        #
        self._app_id: str = app_id
        self._app_name: str = app_name
        self._scenario_id: str = scenario_id
        self._scenario_name: str = scenario_name
        self._scenario_path: str = scenario_path
        self._exec_mode: str = exec_mode
        self._test_mode: bool = test_mode
        self._test_attach_dir: str = test_attach_dir
        self._test_cfile_path: str = test_cfile_path
        self._work_dir: str = os.path.abspath(work_dir)
        self._app = app
        self._slow_tasks_monitor = slow_tasks_monitor or SlowTasksMonitor.default()

        #
        if force_wdir_to_temp is not None:
            warn("A custom AppInterface subclass is setting `force_wdir_to_temp` - this parameter does nothing "
                 "and will be removed in a future release of the `xpressinsight` package", category=DeprecationWarning)
        if tmp_dir is not None:
            warn("A custom AppInterface subclass is setting `tmp_dir` - this parameter does nothing "
                 "and will be removed in a future release of the `xpressinsight` package", category=DeprecationWarning)

    # pylint: disable-next=unused-argument
    def _init_rest(self, port: int, token: str):
        """ Initialize communication with apprunner over REST. """
        warn(f"REST port and token passed to AppInterface subclass {self.__class__.__name__}; will be ignored")

    @property
    @abstractmethod
    def work_dir(self) -> str:
        """
        Read-only property for the internal working directory of the `xpressinsight` package.

        Returns
        -------
        work_dir : str
            Absolute path to the internal working directory of the `xpressinsight` package.
        """

    @abstractmethod
    def delete_work_dir(self):
        """
        Delete the internal working directory of the `xpressinsight` package.

        See Also
        --------
        AppInterface.work_dir

        Notes
        -----
        In test mode, this function deletes the internal working directory. It is recommended to call this function
        at the beginning of a test, such that the test does not load data from the working directory of a previous
        test run.

        If the working directory does not exist, the function returns immediately. If the working
        directory cannot be deleted, e.g., because another application has a lock on a file, the function
        raises an exception.

        Setting this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with
        a runtime error.
        """

    @property
    @abstractmethod
    def test_mode(self) -> bool:
        """
        Read-only property to check whether the Insight application is running in test mode or in Insight.

        Returns
        -------
        test_mode : bool
            `True` if the application is executed in test mode and `False` if it is running in Insight.

        Notes
        -----
        When the application is running in Insight, then the value is `False`, otherwise the value is `True`.
        """

    @property
    @abstractmethod
    def exec_mode(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the execution mode in which Xpress Insight is running the model. :index-name:`run mode`

        Returns
        -------
        exec_mode : str
            The name of the current execution mode, as specified in the execution mode decorators.
            This can be a user-defined value, or can be one of these pre-defined standard values:
            `ExecMode.LOAD` (when a scenario is being loaded),
            `ExecMode.RUN`  (when a scenario is being run),
            `ExecMode.NONE` (when the application is being executed outside of Xpress Insight
                                and no execution mode function is currently being executed).

        Examples
        --------
        Demonstration of setting the execution mode (test mode only).

        >>> insight.exec_mode = 'CALCULATE_STATS'

        Demonstration of getting the execution mode then outputting it.

        >>> print('execution mode = ', insight.exec_mode)
        execution mode = CALCULATE_STATS

        Notes
        -----
        The `exec_mode` property can only be set in test mode.

        In the `LOAD` execution mode function (or other user-defined execution modes with `clear_input=True`)
        your app should initialize its input data.
        In the `RUN` execution mode function (or user-defined execution modes with `clear_input=False`)
        it should then initialize its result data.

        Used to mock the execution mode that requested the scenario execution, when testing code outside of an Insight
        scenario. By default, :fct-ref:`insight.exec_mode` will be initialized automatically if you call an execution
        mode function. However, if you want to test another function, which is not an execution mode function,
        then it could make sense to set the `exec_mode` property manually.

        Modifying this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a
        runtime error.
        """

    @exec_mode.setter
    @abstractmethod
    def exec_mode(self, exec_mode: str):
        pass

    @property
    @abstractmethod
    def app_id(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the id of the Xpress Insight application which is the parent of the model.

        Returns
        -------
        app_id : str
            The UID of the Xpress Insight application.

        Examples
        --------
        Demonstration of setting the application ID (test mode only).

        >>> insight.app_id = 'xyzzy'

        Demonstration of getting the application ID then outputting it.

        >>> print('app id = ', insight.app_id)
        app id = xyzzy

        Notes
        -----
        The `app_id` property can only be set in test mode.

        In test mode can be used to mock the Insight application state when testing code outside of an Insight scenario.

        Modifying this property when `insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

    @app_id.setter
    @abstractmethod
    def app_id(self, new_app_id: str):
        pass

    @property
    @abstractmethod
    def app_name(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the name of the Xpress Insight application which is the parent of the model.

        Returns
        -------
        app_name : str
            The name of the application.

        Examples
        --------
        Demonstration of setting the application name (test mode only).

        >>> insight.app_name = 'My App'

        Demonstration of getting the application name then outputting it.

        >>> print('app name = ', insight.app_name)
        app name = My App

        Notes
        -----
        The `app_name` property can only be set in test mode.

        The application name is not related to the name defined in the model's source code.

        Used to mock the Insight application state when testing code outside of an Insight scenario.

        Modifying this property when `insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

    @app_name.setter
    @abstractmethod
    def app_name(self, new_app_name: str):
        pass

    @property
    @abstractmethod
    def username(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the username of the Insight user that initiated the current scenario execution.
        :index-name:`Insight user name`

        Returns
        -------
        username : str
            The user name.

        Examples
        --------
        Demonstration of setting the user name (test mode only).

        >>> insight.username = 'LouisXIV'

        Demonstration of getting the user name then outputting it.

        >>> print('user name = ', insight.username)
        user name = LouisXIV

        Notes
        -----
        The `username` property can only be set in test mode.

        When called while the model is not running within Insight, this returns `DEV`.

        The username returned will be the username suitable for human display - be aware that this is
        not a unique identifier for the user's account, as users can change their names.

        Used to mock the user who requested the scenario execution, when testing code outside of an Insight scenario.

        Modifying this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a
        runtime error.
        """

    @username.setter
    @abstractmethod
    def username(self, new_username: str):
        pass

    @property
    @abstractmethod
    def user_id(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the user ID of the Insight user that initiated the current scenario execution.
        :index-name:`Insight user ID`

        Returns
        -------
        user_id : str
            The identifier for an user.

        Examples
        --------
        Demonstration of setting the user ID (test mode only).

        >>> insight.user_id = 'userid123456789'

        Demonstration of getting the user ID then outputting it.

        >>> print('user_id = ', insight.user_id)
        user_id = userid123456789

        Notes
        -----
        The `user_id` property can only be set in test mode.

        When called while the model is not running within Insight, this returns `f3c92ab3-6996-4b4b-87c9-f5a146019c51`.

        Used to mock the user ID of the user who requested the scenario execution, when testing code outside an
        Insight scenario.

        Modifying this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a
        runtime error.
        """

    @user_id.setter
    @abstractmethod
    def user_id(self, new_user_id: str):
        pass

    @property
    @abstractmethod
    def test_cfile_path(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the location of the app companion file to parse, when in test mode.

        Returns
        -------
        cfile_path : str
            The path to the app companion file.

        Examples
        --------
        Demonstration of setting the companion file path (test mode only).

        >>> insight.test_cfile_path = 'C:/dev/app/application.xml'

        Demonstration of getting the companion file path (test mode only).

        >>> print(insight.test_cfile_path)
        """

    @test_cfile_path.setter
    @abstractmethod
    def test_cfile_path(self, cfile_path: str):
        pass

    @property
    @abstractmethod
    def test_attach_dir(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the location to store mock attachments for app and scenario, when in test mode.

        Returns
        -------
        attach_dir : str
            The path to the attachments directory.

        Examples
        --------
        Demonstration of setting the attachment directory (test mode only).

        >>> insight.test_attach_dir = 'C:/dev/appattachments'

        Demonstration of getting the attachment directory (test mode only).

        >>> print(insight.test_attach_dir)

        See Also
        --------
        AppInterface.test_app_attach_dir
        AppInterface.test_scen_attach_dir
        """

    @test_attach_dir.setter
    @abstractmethod
    def test_attach_dir(self, attach_dir: str):
        pass

    @property
    @abstractmethod
    def test_app_attach_dir(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the path to use for the attachments directory of the current app, when in test mode.

        Returns
        -------
        app_attach_dir : str
            The path to the app attachments directory.

        Examples
        --------
        Demonstration of getting the app attachment directory (test mode only).

        >>> print(insight.test_app_attach_dir)

        Demonstration of setting the app attachment directory (test mode only).

        >>> insight.test_app_attach_dir = 'C:/dev/appattachments'

        Notes
        -----
        When you set a path using this function, it will be used instead of the `appattach` subdirectory of
        the directory specified by :param-ref:`insight.test_attach_dir` property.

        Setting this propery when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a
        runtime error.

        See Also
        --------
        AppInterface.test_attach_dir
        AppInterface.test_scen_attach_dir
        """

    @test_app_attach_dir.setter
    @abstractmethod
    def test_app_attach_dir(self, app_attach_dir: str):
        pass

    #
    @property
    @abstractmethod
    def test_scen_attach_dir(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the path to use for the scenario attachments directory of the current scenario.

        Returns
        -------
        scen_attach_dir : str
            The path to the scenario attachments directory.

        Examples
        --------
        Demonstration of setting scenario attachment directory (test mode only).

        >>> insight.test_scen_attach_dir = 'C:/dev/scenattachments'

        Demonstration of getting scenario attachment directory (test mode only).

        >>> print(insight.test_scen_attach_dir)

        Notes
        -----
        When you set a path using this function, it will be used instead of the `scenattach` subdirectory of
        the directory specified by :param-ref:`insight.test_attach_dir` property.

        Setting this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a
        runtime error.

        See Also
        --------
        AppInterface.test_attach_dir
        AppInterface.test_app_attach_dir
        """

    @test_scen_attach_dir.setter
    @abstractmethod
    def test_scen_attach_dir(self, scen_attach_dir: str):
        pass

    #
    @abstractmethod
    def set_attach_tags(self, new_tags: List[AttachTag]):
        #
        # noinspection PyUnresolvedReferences
        """
        Sets the list of tags that can be used in attachments

        Parameters
        ----------
        new_tags : List[AttachTag]
            List of populated `insightattachmenttag` records.

        Examples
        --------
        Demonstration of setting the available tags

        >>> insight.set_attach_tags([
        ...     AttachTag(name='first', usage=AttachTagUsage.SINGLE_FILE),
        ...     AttachTag(name='test', usage=AttachTagUsage.MULTI_FILE),
        ... ])

        Notes
        -----
        Used to mock the available attachment tags when testing code outside of an Insight scenario.

        The `AttachTagUsage.SINGLE_FILE` usage constraint will only be applied during future calls to modify
        attachment tags.  It will not be applied to attachments that are already tagged when `insight.set_attach_tags`
        is called.

        Setting this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a
        runtime error.

        See Also
        --------
        AppInterface.list_attach_tags
        AppInterface.set_attach_tags
        """

    @abstractmethod
    def set_attach_rules(self, new_rules: AttachmentRules):
        #
        # noinspection PyUnresolvedReferences
        """
        Sets the 'rules' used to validate attachments and attachment meta-data.

        Parameters
        ----------
        new_rules : AttachmentRules
            Populated `insightattachmentrules` record

        Examples
        --------
        Demonstration of setting the example rules

        >>> insight.set_attach_rules(AttachmentRules(
        ...     max_size=1*1024*1024,
        ...     max_attach_count=25,
        ...     max_filename_len=32,
        ...     invalid_filename_chars=['/', r'\', ' '],
        ...     max_description_len=128,
        ... ))

        Notes
        -----
        Used to change the rules that are applied to new attachments - for example, if you want to test how your
        code responds to the `AttachStatus.TOO_MANY` error code without actually creating a lot of attachments, you can
        use this procedure to set a lower number of attachments per scenario.

        Setting this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a
        runtime error.
        """

    @property
    @abstractmethod
    def raise_attach_exceptions(self) -> Optional[bool]:
        """
        Property indicating whether to raise an exception on an attachment-related error (such as attempting
        to get an attachment that doesn't exist, or putting an attachment too large to be accepted by Insight).

        Notes
        -----
        When set to `False` or `None`, the caller must check the `attach_status` property after every attachment
        operation to detect errors.

        This value will initially be inherited from the configuration of the app, but can be modified during
        app execution, for example for calling a library that does not support raising attachment exceptions.

        See Also
        --------
        AppConfig.__init__
        AppInterface.attach_status
        """

    @raise_attach_exceptions.setter
    @abstractmethod
    def raise_attach_exceptions(self, raise_attach_exceptions: Optional[bool]):
        pass

    @property
    @abstractmethod
    def attach_status(self) -> AttachStatus:
        """
        Property indicating the status of the most recent attempt to access or modify an attachment on the
        current thread. Setting this property will only change the value returned by future reads from this current
        thread.

        It's recommended that apps should set the `raise_attach_exceptions` attribute of either the `AppConfig` or
        `AppInterface` class to `True`, which removes the need to check the `attach_status` property.`
        :index-name:`attachment operation error codes`

        See Also
        --------
        AttachStatus
        AppConfig.raise_attach_exceptions
        AppInterface.raise_attach_exceptions
        AppInterface.get_scen_attach
        AppInterface.list_scen_attach
        AppInterface.list_scen_attach_by_tag
        AppInterface.put_scen_attach
        AppInterface.rename_scen_attach
        AppInterface.scen_attach_info
        AppInterface.set_scen_attach_desc
        AppInterface.set_scen_attach_hidden
        AppInterface.set_scen_attach_tags
        AppInterface.get_app_attach
        AppInterface.list_app_attach
        AppInterface.list_app_attach_by_tag
        AppInterface.app_attach_info

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to an attachment-related function or procedure, you should
        check the value of `insight.attach_status` to see if your request succeeded.

        The `attach_status` property may not be set to `AttachStatus.IN_PROGRESS`.
        """

    @attach_status.setter
    @abstractmethod
    def attach_status(self, status: AttachStatus):
        pass

    #
    #

    #
    @abstractmethod
    def list_attach_tags(self) -> List[AttachTag]:
        #
        # noinspection PyUnresolvedReferences
        """
        Retrieves a list of the attachment tags defined in the companion file. :index-name:`list attachment tags`

        Returns
        -------
        attach_tags : List[AttachTag]
            A list of the defined tags.

        Raises
        ------
        AttachError
            If there is an error listing the tags.

        Examples
        --------
        Example of outputting list of tags defined in companion file

        >>> tags = insight.list_attach_tags()

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        See Also
        --------
        AppInterface.set_scen_attach_tags
        """

    @abstractmethod
    def get_scen_attach(self, filename: str, scenario_path: str = None, *, destination_filename: str = None) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Retrieves an attachment from the Insight server for a given scenario, placing it in a location where it can be
        read by the model. :index-name:`get scenario attachment`

        Parameters
        ----------
        filename : str
            The filename of the attachment to be retrieved.
        scenario_path : str
            The path of a scenario. A scenario path is the full path to a scenario name starting from the repository
            root and including the app name. E.g. `/myapp/DirA/myscenario`
            If the scenario path is not specified, the attachment is retrieved for the current scenario.
        destination_filename : Optional[str]
            The local filename to which to write the attachment content; may be an absolute path or relative to the
            Python working directory. If not specified, the attachment will be written to a file in the working
            directory.

        Raises
        ------
        AttachNotFoundError
            If an attachment with this name cannot be found in the targetted scenario.
        AttachError
            If there is some other error fetching the attachment.

        Examples
        --------
        Example of copying a scenario attachment called `my_attach.dat` to the working directory.

        >>> insight.get_scen_attach('my_attach.dat')
        ... with open('my_attach.dat') as f:
        ...     pass  # process the file

        Getting an attachment for the current scenario.

        >>> insight.get_scen_attach('my_attach.dat', '/myapp/DirA/myscenario')
        ... with open('my_attach.dat') as f:
        ...     pass  # process the file

        Getting an attachment for a scenario with path `/myapp/DirA/myscenario`.

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.put_scen_attach
        """

    @abstractmethod
    def put_scen_attach(self, filename: str, overwrite: bool = True, *, source_filename: str = None) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Uploads a scenario attachment to the Insight server. :index-name:`put scenario attachment`

        Parameters
        ----------
        filename : str
            The filename of the attachment to be uploaded
        overwrite : bool
            If `True`, will overwrite attachment if it already exists.  If `False`
            and attachment already exists, will fail. Defaults to `True` if not given.
        source_filename : Optional[str]
            The local filename from which to read the attachment content; may be an absolute path or relative to the
            Python working directory. If not specified, the attachment will be read from a file in the working
            directory.

        Raises
        ------
        AttachFilenameInvalidError
            If the given filename is not valid for an attachment
        AttachAlreadyExistsError
            If an attachment with this name already exists and the `overwrite` flag was not passed as `True`
        AttachTooLargeError
            If the file is too large to add as an attachment
        TooManyAttachError
            If the scenario already has too many attachments
        AttachError
            If there is some other error adding the attachment

        Examples
        --------
        Example of taking a file `my_attach.dat` in the working directory, and saving it as a new scenario attachment
        called `my_attach.dat`.

        >>> try:
        ...     insight.put_scen_attach('my_attach.dat', False)
        ...     print("Attachment added ok")
        ....except AttachAlreadyExistsError:
        ...     print("Attachment already exists")

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        The new attachment will not be available on the Insight server until the scenario completes.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.get_scen_attach
        """

    @abstractmethod
    def delete_scen_attach(self, filename: str) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Deletes a scenario attachment. :index-name:`delete scenario attachment`

        Parameters
        ----------
        filename : str
            The filename of the attachment to be deleted.

        Raises
        ------
        AttachNotFoundError
            If the specified attachment was not found on the scenario.
        AttachError
            If there is some other error deleting the attachment.

        Examples
        --------
        Example of deleting an attachment called `my_attach.dat` from the current scenario.

        >>> insight.delete_scen_attach('my_attach.dat')

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        The attachment will still be available on the Insight server until the scenario completes.

        Attempting to access attachments outside of an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        """

    @abstractmethod
    def rename_scen_attach(self, old_name: str, new_name: str) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Renames an existing scenario attachment.

        Parameters
        ----------
        old_name : str
            The existing filename of the attachment to be renamed
        new_name : str
            The new filename of the attachment.  Must not already be used for a scenario attachment.
            :index-name:`rename scenario attachment`

        Raises
        ------
        AttachNotFoundError
            If the specified attachment was not found on the scenario.
        AttachFilenameInvalidError
            If the given new attachment name was invalid
        AttachAlreadyExistsError
            If the given new attachment name is already in use
        AttachError
            If there is some other error renaming the attachmnet.

        Examples
        --------
        Example of renaming an existing attachment of the current scenario from `my_attach.dat` to `my_attach-2015.dat`.

        >>> insight.rename_scen_attach('my_attach.dat', 'my_attach-2015.dat')

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        The attachment will not be renamed on the Insight server until the scenario completes.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        """

    @abstractmethod
    def set_scen_attach_desc(self, filename: str, description: str) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Update the description of an existing scenario attachment. :index-name:`set scenario attachment description`

        Parameters
        ----------
        filename : str
            The filename of the scenario attachment to update
        description : str
            The new description of the attachment

        Raises
        ------
        AttachNotFoundError
            If the specified attachment was not found on the scenario.
        AttachInvalidDescriptionError
            If the given description is not valid.
        AttachError
            If there is some other error updating the description.

        Examples
        --------
        Example of setting the description of a scenario attachment `my_attach.dat` to be "`This is my first
        attachment`"

        >>> insight.set_scen_attach_desc('my_attach.dat',
        ...                              'This is my attachment')

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        The attachment will not be updated on the Insight server until the scenario completes.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        """

    @abstractmethod
    def set_scen_attach_tags(self, filename: str, tags: List[str]) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Update the tags of an existing scenario attachment. :index-name:`set scenario attachment tags`

        Parameters
        ----------
        filename : str
            The filename of the scenario attachment to update.
        tags : List[str]
            The new tags to apply to the attachment.  Any existing tags will be removed.

        Raises
        ------
        AttachNotFoundError
            If the specified attachment was not found on the scenario.
        AttachTagsInvalidError
            If the requiested attachment tags are invalid.
        AttachError
            If there is some other error updating the attachment tags.

        Examples
        --------
        Example of setting the tags of a scenario attachment `my_attach.dat` to be "mytag1" and "mytag2"

        >>> insight.set_scen_attach_tags('my_attach.dat',
        ...                              ['mytag1', 'mytag2'])

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        The attachment will not be updated on the Insight server until the scenario completes.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        If any of the specified tags are single-file tags, they will be removed from other scenarios as part of this
        operation.

        See Also
        --------
        AppInterface.attach_status
        """

    @abstractmethod
    def set_scen_attach_hidden(self, filename: str, hidden: bool) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Mark an existing scenario attachment as hidden or visible in the Xpress Insight UI.
        :index-name:`set scenario attachment hidden`

        Parameters
        ----------
        filename : str
            The filename of the scenario attachment to hide or show.
        hidden : bool
            If `True`, the attachment will be hidden in the Xpress Insight UI; if `False`, it will be visible.

        Raises
        ------
        AttachNotFoundError
            If the specified attachment was not found on the scenario.
        AttachError
            If there is some other error updating the 'hidden' flag.

        Examples
        --------
        Example of hiding of a scenario attachment `my_attach.dat`

        >>> insight.set_scen_attach_hidden('my_attach.dat', True)

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        The attachment will not be updated on the Insight server until the scenario completes.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        """

    @abstractmethod
    def list_scen_attach(self, scenario_path: str = None) -> List[Attachment]:
        #
        # noinspection PyUnresolvedReferences
        """
        Retrieves a list of all the files attached to a given scenario. :index-name:`list scenario attachments`

        Parameters
        ----------
        scenario_path : str, optional
            The path of a scenario. A scenario path is the full path to a scenario name starting from the repository
            root and including the app name. E.g. `/myapp/DirA/myscenario`
            If the scenario path is not specified, the attachment is retrieved for the current scenario

        Returns
        -------
        attachments : List[Attachment]
            A list of the scenario attachments.

        Raises
        ------
        AttachError
            If there is some error listing the attachments.

        Examples
        --------
        Example of fetching information about all attachments of a scenario into a list called `atts`

        >>> atts = insight.list_scen_attach()

        Getting the list of attachments for the current scenario

        >>> atts = insight.list_scen_attach('/myapp/DirA/myscenario')

        Getting the list of attachments for a scenario with path `/myapp/DirA/myscenario`

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.get_scen_attach
        AppInterface.list_scen_attach_by_tag
        """

    @abstractmethod
    def list_scen_attach_by_tag(
            self, tag: str, scenario_path: str = None
    ) -> List[Attachment]:
        #
        # noinspection PyUnresolvedReferences
        """
        Retrieves a list of all the files attached to a scenario with the given tag.
        :index-name:`list scenario attachments by tag`

        Parameters
        ----------
        tag : str
            The tag to search for
        scenario_path : str
            The path of a scenario. A scenario path is the full path to a scenario name starting from the repository
            root and including the app name. E.g. `/myapp/DirA/myscenario`.
            If the scenario path is not specified, the attachment is retrieved for the current scenario.

        Returns
        -------
        attachments : List[Attachment]
            A list of the scenario attachments.

        Raises
        ------
        AttachError
            If there is some error listing the attachments

        Examples
        --------
        Example of fetching information about all attachments on a scenario with the tag `tag1` into a list
        called `atts`:

        >>> atts = insight.list_scen_attach_by_tag('mytag1')

        Getting the list of attachments for the current scenario with the given tag.

        >>> atts = insight.list_scen_attach_by_tag('mytag1',
        ...                                        '/myapp/DirA/myscenario')

        Getting the list of attachments with the given tag for a scenario with path `/myapp/DirA/myscenario`.

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.get_scen_attach
        AppInterface.list_scen_attach
        """

    @abstractmethod
    def scen_attach_info(self, filename: str) -> Optional[Attachment]:
        #
        # noinspection PyUnresolvedReferences
        """
        Retrieves information about a given scenario attachment. :index-name:`query scenario attachment`

        Parameters
        ----------
        filename : str
            The filename of the scenario attachment to request

        Returns
        -------
        attachment : Optional[Attachment]
            Information about the attachment.

        Raises
        ------
        AttachNotFoundError
            If the specified attachment was not found on the scenario.
        AttachError
            If there is some other error querying the attachment.

        Examples
        --------
        Example of copying information about the attachment `my_attach.dat` on the current scenario into a record
        called `my_attachment`

        >>> my_attachment = insight.scen_attach_info('my_attach.dat')
        ... print("Attachment description: ", my_attachment.description)

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.set_scen_attach_desc
        """

    @abstractmethod
    def get_app_attach(self, filename: str, *, destination_filename: str = None) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Retrieves an app attachment from the Insight server, placing in a location where it can be
        read by the model. :index-name:`get app attachment`

        Parameters
        ----------
        filename : str
            The filename of the attachment to be retrieved.
        destination_filename : Optional[str]
            The local filename to which to write the attachment content; may be an absolute path or relative to the
            Python working directory. If not specified, the attachment will be written to a file in the working
            directory.

        Raises
        ------
        AttachNotFoundError
            If the specified attachment was not found on the scenario.
        AttachError
            If there is some other error getting the attachment.

        Examples
        --------
        Example of copying an app attachment called `my_attach.dat` to the working directory.

        >>> insight.get_app_attach('my_attach.dat')
        ... with open('my_attach.dat') as f:
        ...    pass  # process the file

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        """

    @abstractmethod
    def list_app_attach(self) -> List[Attachment]:
        #
        # noinspection PyUnresolvedReferences
        """
        Retrieves a list of all the files attached to the app. :index-name:`list app attachments`

        Returns
        -------
        attachments : List[Attachment]
            A list of the app attachments.

        Raises
        ------
        AttachError
            If there is some error listing attachments

        Examples
        --------
        Example of fetching information about all attachments on the app containing the current scenario into a list
        called `atts`

        >>> atts = insight.list_app_attach()
        ... print("Attachments: ", atts)

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.app_attach_info
        AppInterface.get_app_attach
        AppInterface.list_app_attach_by_tag
        """

    @abstractmethod
    def list_app_attach_by_tag(self, tag: str) -> List[Attachment]:
        #
        # noinspection PyUnresolvedReferences
        """
        Retrieves a list of all the files attached to the app with the given tag.
        :index-name:`list app attachments by tag`

        Parameters
        ----------
        tag : str
            The tag to search for

        Returns
        -------
        attachments : List[Attachment]
            A list of the app attachments.

        Raises
        ------
        AttachError
            If there is some error listing the attachments.

        Examples
        --------
        Example of fetching information about all attachments on the app with the tag `tag1` into a list called `atts`

        >>> atts = insight_list_app_attach_by_tag('mytag1')
        ... print("Attachments: ", atts)

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.get_app_attach
        AppInterface.list_app_attach
        """

    @abstractmethod
    def app_attach_info(self, filename: str) -> Optional[Attachment]:
        #
        # noinspection PyUnresolvedReferences
        """
        Retrieves information about a given app attachment. :index-name:`query app attachment`

        Parameters
        ----------
        filename : str
            The filename of the app attachment to request

        Raises
        ------
        AttachNotFoundError
            If the specified attachment was not found on the scenario.
        AttachError
            If there is some other error querying the attachment.

        Returns
        -------
        attachment : Optional[Attachment]
            Information about the attachment.

        Examples
        --------
        Example of copying information about the attachment `my_attach.dat` on the app containing the current
        scenario into a record called `my_attachment`

        >>> my_attachment = insight.app_attach_info('my_attach.dat')
        ... print("Attachment description: ", my_attachment.description)

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        """

    @abstractmethod
    def get_attachs_by_tag(self, tag: str, *, destination_directory: str = None) -> Optional[List[Attachment]]:
        #
        # noinspection PyUnresolvedReferences
        """
        Gets Insight attachments by tag.

        Searches the scenario and the containing app for an attachment or attachments with the given tag, and
        retrieves them from the Insight server, placing them in a local directory where they can be read by
        the model. If any scenario attachments with the given tag are found, these are retrieved without searching
        the app. If no scenario attachments with the given tag are found, then the search continues at the
        app level. :index-name:`get attachments by tag`

        Parameters
        ----------
        tag : str
            The tag to search for
        destination_directory : str
            The directory into which to copy the attachments, which must exist or a `FileNotFoundError` will be raised.
            If not specified, the attachments will be copied into the Python working directory.

        Raises
        ------
        AttachError
            If there is some error querying the attachments

        Returns
        -------
        attachments : Optional[List[Attachment]]
            A list which will be populated with the details of the attachments that were retrieved.

        Examples
        --------
        Example of searching for and retrieving all attachments with the tag `tag1`

        >>> attachments = insight.get_attachs_by_tag('mytag1')
        ... for a in attachments:
        ...     print(a.filename)

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.list_scen_attach
        AppInterface.list_app_attach
        AppInterface.get_app_attach
        AppInterface.get_scen_attach
        """

    @abstractmethod
    def get_attach_by_tag(self, tag: str, *, destination_directory: str = None) -> Optional[Attachment]:
        #
        # noinspection PyUnresolvedReferences
        """
        Gets Insight attachments by tag

        Searches the scenario and the containing app for an attachment or attachments with the given tag, and
        retrieves them from the Insight server, placing them in a local directory directory where they can be read by
        the model. If any scenario attachments with the given tag are found, these are retrieved without searching
        the app. If no scenario attachments with the given tag are found, then the search continues at the
        app level. :index-name:`get attachments by tag`

        Parameters
        ----------
        tag : str
            The tag to search for
        destination_directory : str
            The directory into which to copy the attachment, which must exist or a `FileNotFoundError` will be raised.
            If not specified, the attachment will be copied into the Python working directory.

        Returns
        -------
        attachment : Optional[Attachment]
            An attachment object which will be populated with the details of the attachment that was retrieved.

        Raises
        ------
        AttachNotFoundError
            If the no attachment was not found with the given tag
        SeveralAttachFoundError
            If more than one attachment was found with the given tag
        AttachError
            If there is some other error querying the attachments

        Examples
        --------
        Example of searching for and retrieving an attachment with the tag `tag1`

        >>> attachment = insight.get_attach_by_tag('mytag1')
        ... with open(attachment.filename) as f:
        ...     pass  # process the file

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.list_scen_attach
        AppInterface.list_app_attach
        AppInterface.get_app_attach
        AppInterface.get_scen_attach
        """

    @abstractmethod
    def get_attach_filenames_by_tag(self, tag: str, *, destination_directory: str = None) -> List[str]:
        #
        # noinspection PyUnresolvedReferences
        """
        Gets Insight attachments by tag

        Searches the scenario and the containing app for an attachment or attachments with the given tag, and
        retrieves them from the Insight server, placing them in a local directory where they can be read by
        the model. If any scenario attachments with the given tag are found, these are retrieved without searching
        the app. If no scenario attachments with the given tag are found, then the search continues at the
        app level. :index-name:`get attachments by tag`

        Parameters
        ----------
        tag : str
            The tag to search for
        destination_directory : str
            The directory into which to copy the attachments, which must exist or a `FileNotFoundError` will be raised.
            If not specified, the attachments will be copied into the Python working directory.

        Raises
        ------
        AttachError
            If there is some other error querying the attachments.

        Returns
        -------
        filenames : List[str]
            A list which will be populated with the filenames of the attachments that were retrieved.

        Examples
        --------
        Example of searching for and retrieving an attachment with the tag `tag1`

        >>> filenames = insight.get_attach_by_tag('mytag1')
        ... for f in filenames:
        ...     print(f)

        Notes
        -----
        To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
        `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
        When this is not the case, after every call to this method you should check the value of
        `insight.attach_status` to see if your request succeeded.

        Attempting to access attachments outside an Xpress Insight scenario will access local files that have been
        supplied to this class.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.list_scen_attach
        AppInterface.list_app_attach
        AppInterface.get_app_attach
        AppInterface.get_scen_attach
        """

    @abstractmethod
    def get_attach_rules(self) -> AttachmentRules:
        #
        # noinspection PyUnresolvedReferences
        """
        Retrieves the 'rules' used to validate attachments and attachment meta-data.

        Returns
        -------
        rules : AttachmentRules
            The attachment rules.

        Examples
        --------
        Demonstration of getting the example rules

        >>> rules = insight.get_attach_rules()

        Notes
        -----
        Used to retrieve the rules that are used to validate new attachments - for example, maximum attachment size.

        This will only be necessary if you want to validate new attachments within the model, before they
        trigger Insight attachment errors for violating any of these rules.
        """

    @abstractmethod
    def get_item_info(self, path: str) -> ItemInfo:
        #
        # noinspection PyUnresolvedReferences
        """
        Get information for a repository item with the supplied path.

        Parameters
        ----------
        path : str
            Path to the repository item.

        Returns
        -------
        item_info : ItemInfo
            Information about the repository item (scenario / folder).

        Examples
        --------
        Example of using `get_item_info` to obtain info for a scenario.

        >>> info = insight.get_item_info('/my_app/my_scenario')

        Example of using `get_item_info` with error handling to obtain info for the current scenario.

        >>> @xi.ExecModeLoad()
        ... def load(self):
        ...     try:
        ...         info = self.insight.get_item_info(".")
        ...         print(info)
        ...     except xi.InterfaceError as ex:
        ...         print(ex)

        Notes
        -----
        Raises :fct-ref:`InterfaceError` on failure.

        See Also
        --------
        ItemInfo
        InterfaceError
        AppInterface.get_item_infos
        AppInterface.add_item_info
        AppInterface.clear_item_infos
        """

    @abstractmethod
    def get_item_infos(self, folder_path: str) -> List[ItemInfo]:
        #
        # noinspection PyUnresolvedReferences
        """
        Get information for items in the folder with the supplied path.

        Parameters
        ----------
        folder_path : str
            Path to the repository folder.

        Returns
        -------
        item_info : ItemInfo
            Information about the items (folders / scenarios) in the given folder.
            The function does not return information about Virtual Scenario Groups.

        Examples
        --------
        Example of using `get_item_infos` to obtain info for items in a folder.

        >>> info = insight.get_item_infos('/appname/my_folder')

        Example of using `get_item_infos` with error handling to obtain info for
        items in the same folder as the current scenario.

        >>> @xi.ExecModeLoad()
        ... def load(self):
        ...     try:
        ...         infos = self.insight.get_item_infos(".")
        ...         print(infos)
        ...     except xi.InterfaceError as ex:
        ...         print(ex)

        Notes
        -----
        Raises :fct-ref:`InterfaceError` on failure.

        See Also
        --------
        ItemInfo
        InterfaceError
        AppInterface.get_item_info
        AppInterface.add_item_info
        AppInterface.clear_item_infos
        """

    def add_item_info(self, item_info: ItemInfo) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Adds the given ItemInfo object to the repository of item infos that are used in test mode.

        Parameters
        ----------
        item_info : ItemInfo
            The item information object to add. All object attributes must be populated and the
            `path` and `parent_path` must both be absolute paths.

        Examples
        --------
        Demonstration of adding an item info and clearing the item info dictionary.

        >>> import sys
        ... import xpressinsight as xi
        ...
        ... @xi.AppConfig(name="Item Info Test", scen_types=["SIMULATION"])
        ... class InsightApp(xi.AppBase):
        ...     @staticmethod
        ...     def print_info(info: xi.ItemInfo):
        ...         print('  ItemInfo:')
        ...         print('    name:        ', info.name)
        ...         print('    type:        ', info.type)
        ...         print('    path:        ', info.path)
        ...         print('    parent_path: ', info.parent_path)
        ...
        ...     @xi.ExecModeLoad(descr="Loads input data.")
        ...     def load(self):
        ...         print('Current scenario item info:')
        ...         self.print_info(self.insight.get_item_info("."))
        ...         print('Item infos in application root folder:')
        ...         for item in self.insight.get_item_infos(
        ...                 str(xi.RepositoryPath.encode(
        ...                     [self.insight.app_name]))):
        ...             self.print_info(item)
        ...
        ...     @xi.ExecModeRun(descr="Takes input and computes results.")
        ...     def run(self):
        ...         print("Run mode finished.")
        ...
        ... if __name__ == "__main__":
        ...     # When the application is run in test mode, first initialize
        ...     # the test environment, then execute the load and run modes.
        ...     def add_default_app_folder_item(insight: xi.AppInterface):
        ...         insight.add_item_info(xi.ItemInfo(
        ...             id=insight.app_id,
        ...             name='Root',
        ...             type='FOLDER',
        ...             path=str(xi.RepositoryPath.encode(
        ...                  [insight.app_name])),
        ...             parent_path=str(xi.RepositoryPath.encode(
        ...                  [insight.app_name]))))
        ...
        ...     def add_default_scenario_item(insight: xi.AppInterface,
        ...                                   scen_type: str = 'SCENARIO'):
        ...         insight.add_item_info(xi.ItemInfo(
        ...             id=insight.scenario_id,
        ...             name=insight.scenario_name,
        ...             type=scen_type,
        ...             path=insight.scenario_path,
        ...             parent_path=insight.scenario_parent_path))
        ...
        ...     app = InsightApp()
        ...     add_default_app_folder_item(app.insight)
        ...     add_default_scenario_item(app.insight)
        ...     app.call_exec_mode('LOAD')
        ...
        ...     app.insight.clear_item_infos()
        ...     app.insight.app_name = 'app 1'
        ...     app.insight.scenario_name = 'my_simulation 2021/09'
        ...     app.insight.scenario_path = str(xi.RepositoryPath.encode(
        ...         [app.insight.app_name, 'my_folder',
        ...          app.insight.scenario_name]))
        ...
        ...     add_default_app_folder_item(app.insight)
        ...     app.insight.add_item_info(xi.ItemInfo(
        ...         id='00000000-0000-0000-0000-000000000001',
        ...         name='my_folder',
        ...         type='FOLDER',
        ...         path=str(xi.RepositoryPath.encode(
        ...             [app.insight.app_name, 'my_folder'])),
        ...         parent_path=str(xi.RepositoryPath.encode(
        ...             [app.insight.app_name]))))
        ...     add_default_scenario_item(app.insight, 'SIMULATION')
        ...     app.call_exec_mode('LOAD')

        Notes
        -----
        Used to mock the Insight repository item info when testing code in test mode.

        The model will abort with a runtime error if an item info with the given name or path already exists.

        Calling this procedure when :fct-ref:`AppInterface.test_mode` is <tt>False</tt> will
        cause the model to abort with a runtime error.

        See Also
        --------
        ItemInfo
        AppInterface.test_mode
        AppInterface.get_item_info
        AppInterface.get_item_infos
        AppInterface.clear_item_infos
        """

    def clear_item_infos(self) -> None:
        """
        Removes any ItemInfo objects previously added in test mode.

        Examples
        --------
        See :fct-ref:`AppInterface.add_item_info`.

        Notes
        -----
        Used to reset the list of mock ItemInfo objects that were added by :fct-ref:`AppInterface.add_item_info`.

        Calling this method when :fct-ref:`AppInterface.test_mode` is <tt>False</tt>
        will cause the model to abort with a runtime error.

        See Also
        --------
        ItemInfo
        AppInterface.get_item_info
        AppInterface.get_item_infos
        AppInterface.add_item_info
        """

    #

    #

    @property
    @abstractmethod
    def scenario_id(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the id of the Xpress Insight scenario.

        Returns
        -------
        scenario_id : str
            The UID of the Xpress Insight scenario.

        Examples
        --------
        Demonstration of setting the scenario id (test mode only).

        >>> insight.scenario_id = 'xyzzy'

        Demonstration of getting the scenario id.

        >>> print('scenario id = ', insight.scenario_id)
        scenario id = xyzzy

        Notes
        -----
        The `scenario_id` property can only be set in test mode.

        In test mode can be used to mock the Insight scenario id.

        Modifying this property when `insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

    @scenario_id.setter
    @abstractmethod
    def scenario_id(self, scenario_id: str):
        pass

    @property
    @abstractmethod
    def scenario_name(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the name of the Xpress Insight scenario.


        Returns
        -------
        scenario_name : str
            The name of the Xpress Insight scenario.

        Examples
        --------
        Demonstration of setting the scenario name (test mode only).

        >>> insight.scenario_name = 'Scenario B'

        Demonstration of getting the scenario name.

        >>> print('scenario name = ', insight.scenario_name)
        scenario name = Scenario B

        Notes
        -----
        The `scenario_name` property can only be set in test mode.

        In test mode can be used to mock the Insight scenario name.

        Modifying this property when `insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

    @scenario_name.setter
    @abstractmethod
    def scenario_name(self, scenario_name: str):
        pass

    @property
    @abstractmethod
    def scenario_path(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the path of the Xpress Insight scenario.

        Returns
        -------
        scenario_path : str
            The path of the Xpress Insight scenario.

        Examples
        --------
        Demonstration of setting the scenario path (test mode only).

        >>> insight.scenario_path = '/myapp/DirA/myscenario'

        Demonstration of getting the scenario path.

        >>> print('scenario path = ', insight.scenario_path)
        scenario path = /myapp/DirA/myscenario

        Notes
        -----
        A scenario path is the full path to a scenario name starting from the repository root and including
        the app name. E.g. `/myapp/DirA/myscenario`.

        The `scenario_path` property can only be set in test mode.

        In test mode can be used to mock the Insight scenario path.

        Modifying this property when `insight.test_mode` is `False` will cause the model to abort with a runtime error.

        See Also
        --------
        AppInterface.scenario_parent_path
        """

    @scenario_path.setter
    @abstractmethod
    def scenario_path(self, scenario_path: str):
        #
        # noinspection PyUnresolvedReferences
        pass

    @property
    def scenario_parent_path(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for getting the parent path of the Xpress Insight scenario.

        Returns
        -------
        scenario_parent_path : str
            The parent path of the Xpress Insight scenario.

        Examples
        --------
        Demonstration of getting the scenario parent path.

        >>> print('scenario parent path = ', insight.scenario_parent_path)
        scenario parent path = /myapp/DirA/

        Notes
        -----
        A scenario parent path is the full path to the parent folder of the scenario starting from the repository
        root and including the app name. E.g. `/myapp/DirA`.

        The `scenario_parent_path` property can only be read.
        The parent path is computed with the help of `scenario_path`.

        See Also
        --------
        AppInterface.scenario_path
        """
        scen_path = RepositoryPath(self.scenario_path)
        scen_path.pop()
        return str(scen_path) + '/'

    @abstractmethod
    def get_scenario_data(self, scenario_path_or_id: str, scenario_data_class: Type[SCENARIO_DATA_CONTAINER], *,
                          fetch_individual_series=False) -> SCENARIO_DATA_CONTAINER:
        #
        # noinspection PyUnresolvedReferences
        """
        Loads the entities described in annotations on the given class, from the given scenario, into an
        instance of the given class.

        When fetching data from another scenario or app, you will supply a class that has type attributes
        annotated using the `xpressinsight.data.` or `xpressinsight.types.` helper functions, and is decorated using
        the `ScenarioData` or `AppConfig` decorator. It's recommended to use `ScenarioData` unless the class is the
        application class for the app being read from, as `AppConfig` will perform additional validation that is only
        relevent for application definitions.

        Parameters
        ----------
        scenario_path_or_id : str
            The path or ID of the scenario from which you want to read.
        scenario_data_class : Type
            A class declared with the `ScenarioData` or `AppConfig` decorator.
        fetch_individual_series : bool
            Configures method by which DataFrame entities are fetched from the Insight repository; when `True`, they
            are fetched as an entire frame; when `False` they are fetched as individual series and then combined into
            a DataFrame within the Python runtime. The default (`True`) is more efficient at the expense of using
            more memory in the Insight worker for some scenarios; try setting to `False` if you encounter memory
            errors in the worker when requesting a large data frame.

        Returns
        -------
        scenario_data_container : SCENARIO_DATA_CONTAINER
            An instance of the supplied class, with the annotated fields populated with data fetched from the scenario.

        Raises
        ------
        ScenarioNotFoundError
            If the requested scenario is not found.
        InvalidEntitiesError
            If the annotations in the entity container class do not match the schema of the source scenario.
        InterfaceError
            If there is some other error reading the data from the Insight worker.

        Examples
        --------
        Read some entities from scenario `/MyApp/MyFolder/MyScenario`:

        >>> @xi.ScenarioData()
        ... class EntitiesToRead:
        ...     my_integer: xi.data.Scalar(dtype=xi.integer)
        ...     my_string: xi.data.Scalar()
        ...     my_set: xi.data.Index()
        ...     my_array: xi.data.Series()
        ...     my_table: xi.data.DataFrame(
        ...         columns=[
        ...             xi.data.Column('my_first_column', dtype=xi.real),
        ...             xi.data.Column('my_second_column')])
        ...
        ... my_data = self.insight.get_scenario_data('/MyApp/MyFolder/MyScenario',
        ...                                          EntitiesToRead)
        ... print(f"the integer scalar I read is {my_data.my_integer}")

        See Also
        --------
        AppInterface.set_scenario_test_data
        """

    @abstractmethod
    def set_scenario_test_data(self, scenario_path_or_id: str, scenario_data_class: Type[SCENARIO_DATA_CONTAINER],
                               scenario_data: SCENARIO_DATA_CONTAINER):
        #
        # noinspection PyUnresolvedReferences
        """
        Sets the value that will be returned by requests for scenario data of the given class from the given
        scenario, in test mode.

        Parameters
        ----------
        scenario_path_or_id : str
            The path or ID of the scenario from which you want to read.
        scenario_data_class : Type
            A class declared with the `ScenarioData` or `AppConfig` decorator.
        scenario_data : SCENARIO_DATA_CONTAINER
            An instance of `scenario_data_class` that will be returned by future requests.

        Examples
        --------
        Configure a value to be returned by future calls to `get_scenario_data`:

        >>> @xi.ScenarioData
        ... class EntitiesToRead:
        ...     my_integer: xi.data.Scalar()
        ...     my_string: xi.data.Scalar()
        ...
        ... my_test_data = EntitiesToRead()
        ... my_test_data.my_integer = 123
        ... my_test_data.my_string = "hello"
        ... self.insight.set_scenario_test_data('/MyApp/MyFolder/MyScenario',
        ...                                     EntitiesToRead, my_test_data)

        Notes
        -----
        The `set_scenario_data` method can only be called in test mode. Calling this method when `insight.test_mode`
        is `False` will cause the model to abort with a runtime error.

        See Also
        --------
        AppInterface.get_scenario_data
        """

    @abstractmethod
    def update(self, metric: Metric, value: Union[float, int, ObjSense]) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Sends a progress update notification for a single metric from the model to the Xpress Insight v4 system.

        Parameters
        ----------
        metric : Metric
            The type of metric to update.
        value : Union[float, int, ObjSense]
            The value of the metric to update.

        Examples
        --------
        Notify Insight that the current best solution value is 51.9.

        >>> insight.update(Metric.OBJVAL, 51.9)

        Automatic updating of metrics during optimization can be achieved by calling the update function
        from within a suitable solver callback:

        >>> def on_gap_notify(prob, app):
        ...
        ...     num_sol = prob.attributes.mipsols
        ...     app.insight.update(xi.Metric.NUMSOLS, num_sol)
        ...
        ...     if num_sol == 0:
        ...         # Can only occur when mipabsgapnotifybound is used.
        ...         # Don't call gapnotify again.
        ...         return None, None, None, None
        ...
        ...     objective = prob.attributes.mipobjval
        ...     best_bound = prob.attributes.bestbound
        ...
        ...     if best_bound != 0 or objective != 0:
        ...         gap = abs(objective - best_bound) / \\
        ...               max(abs(best_bound), abs(objective))
        ...     else:
        ...         gap = 0
        ...
        ...     app.insight.update(xi.Metric.OBJVAL, objective)
        ...     app.insight.update(xi.Metric.GAP, gap)
        ...
        ...     if gap > 1e-6:
        ...         new_rel_gap_notify_target = gap - 1e-6
        ...     else:
        ...         # Don't call gapnotify again.
        ...         new_rel_gap_notify_target = -1
        ...
        ...     return new_rel_gap_notify_target, None, None, None

        The above callback can then be attached via the Xpress Python API:

        >>> prob = xp.problem()
        ...
        ... # TODO: Define the optimization problem
        ...
        ... # Optionally reset progress and set the objective sense
        ... self.insight.reset_progress()
        ... self.insight.update(xi.Metric.OBJSENSE, prob.attributes.objsense)
        ...
        ... prob.controls.miprelgapnotify = 1e20
        ... prob.addcbgapnotify(on_gap_notify, self, 0)
        ...
        ... prob.solve()

        Notes
        -----
        This function allows the model to report back progress to the system where it is accessible by a client for
        display.

        This function does nothing if the app is running in Xpress Insight v5 or later.

        See Also
        --------
        AppInterface.reset_progress
        AppInterface.send_progress_update
        Metric
        ObjSense
        """

    @abstractmethod
    def reset_progress(self) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Resets the progress state for each Xpress Insight v4 progress metric back to their initial values.

        Examples
        --------
        Reset the progress state for each progress metric back to their initial values.

        >>> insight.reset_progress()

        Notes
        -----
        The :fct-ref:`insight.update` function can be used to report a number of optimization metrics to the
        Xpress Insight v4 system. This method sends notifications to reset the value for each metric to their
        initial values.

        This function does nothing if the app is running in Xpress Insight v5 or later.

        See Also
        --------
        AppInterface.update
        """

    @abstractmethod
    def send_progress_update(self) -> None:
        """
        Stores the current values of the progress entities into the Xpress Insight v5 scenario.

        Notes
        -----
        The progress entities are entities in the Insight scenario defined with `update_progress` attribute `True`.

        When the execution mode was not defined with `send_progress` attribute being `True`, this function does nothing.

        When called from test mode, this function simulates the export of the progress entities.

        In the event of the progress update being rejected by the Insight server, an error will output to the
        run log but the model will not be terminated.
        """

    @abstractmethod
    def get_messages(self) -> Generator[str, None, None]:
        #
        # noinspection PyUnresolvedReferences
        """
        Returns a generator for reading the messages sent to the scenario.

        See Also
        --------
        AppInterface.put_messages

        Examples
        --------
        Read messages and display them until there are none left:

        >>> for msg in insight.get_messages():
        ...     print("Received message: ", msg)

        Notes
        -----
        Messages are typically sent from views as a way to inform an executing scenario of a user action.

        The format of a message is not defined, beyond being a string.

        When test mode has been activated, this function will return messages from a queue populated by the
        :fct-ref:`insight.put_messages` method.
        """

    @abstractmethod
    def put_messages(self, *msgs: str) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Appends one or more messages to the tail of the messages queue, in test mode.
        These messages will be retrieved by a future call to :fct-ref:`insight.get_messages`.

        Examples
        --------
        Populate the queue with messages "one", "two", "three", "four", "five":

        >>> insight.put_messages("one")
        ... insight.put_messages("two")
        ... insight.put_messages("three", "four", "five")

        Notes
        -----
        The `put_messages` method can only be called in test mode.  Calling this method when `insight.test_mode` is
        `False` will cause the model to abort with a runtime error.

        In test mode can be used to mock messages that would be sent by a view.

        See Also
        --------
        AppInterface.get_messages

        """

    @property
    @abstractmethod
    def version(self) -> str:
        #
        # noinspection PyUnresolvedReferences
        """
        Property for the version number of the Insight server that is executing the scenario.

        Returns
        -------
        version : str
            The version of the Insight server, e.g. '5.3.1'.

        Examples
        --------
        Demonstration of setting the Insight server version (test mode only).

        >>> insight.version = '5.3.1'

        Demonstration of getting the Insight server version ID then outputting it.

        >>> print('version = ', insight.version)

        Notes
        -----
        When the scenario is being executed by Insight 4, the `version` property will always be '4'.

        The `version` property can only be set in test mode.

        In test mode can be used to mock the value of the `version` property.

        Modifying this property when `insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

    @version.setter
    @abstractmethod
    def version(self, new_insight_version: str):
        pass

    @abstractmethod
    def get_insight_context(self, environment: Optional[str] = None) -> InsightContext:
        #
        # noinspection PyUnresolvedReferences
        """
        Retrieves information about the context in which the app is currently executing (e.g. information about
        the Insight server and the DMP solution), including an authorization token if the app is executing in DMP.

        Parameters
        ----------
        environment : Optional[str]
            The DMP lifecycle environment for which to request an authorization token (e.g. "design"). If not specified,
            a token for the component's current environment is returned instead. Where the DMP solution has been
            configured with lifecycle isolation, only a token for the current or a lower lifecycle can be requested.
            Will be ignored when the app is not running in DMP.

        Returns
        -------
        context : InsightContext
            The Insight execution context object.

        Examples
        --------
        Demonstration of getting the DMP Manager URL from the context

        >>> context = insight.get_insight_context()
        >>> if context.dmp:
        >>>   print("DMP Manager URL: " + context.dmp.manager_url)
        >>> else:
        >>>   print("Not executing in DMP")

        Notes
        -----
        Raises :fct-ref:`InterfaceError` if passed an unrecognized or unavailable environment.

        Used to retrieve information the app can use to reach outside itself - for example, to query the Insight server
        via its REST API, or to communicate with other DMP services in the same solution.

        When test mode has been activated, this function will return an object previously specified by the
        :fct-ref:`insight.set_insight_context` method, or a default context object if none was specified.
        """

    @abstractmethod
    def set_insight_context(self, context: InsightContext) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Sets the value that will be returned by queries for the InsightContext, in test mode. This value will be
        returned regardless of the environment requested by get_insight_context (since the environment only affects
        the solution token, not any of the other fields).

        Parameters
        ----------
        context : InsightContext
            The context information to be returned in test mode.

        Examples
        --------
        Configure an `InsightContext` to be returned by future calls to `get_insight_context()`:

        >>> context = xi.InsightContext(insight_url="http://localhost:8080/")
        >>> insight.set_insight_context(context)

        Notes
        -----
        The `set_insight_context` method can only be called in test mode. Calling this method when `insight.test_mode`
        is `False` will cause the model to abort with a runtime error.

        See Also
        --------
        AppInterface.get_insight_context
        """

    @abstractmethod
    def get_solution_database(self) -> SolutionDatabase:
        #
        # noinspection PyUnresolvedReferences
        """
        Retrieves information about the solution database for the current DMP solution.

        Returns
        -------
        solution_database : SolutionDatabase
            An object containing location and credentials for the solution database.

        Examples
        --------
        Demonstration of getting the solution database credentials:

        >>> solution_database = insight.get_solution_database()

        Notes
        -----
        Raises :fct-ref:`InterfaceError` if called when the app is not running in DMP.

        When test mode has been activated, this function will return an object previously specified by the
        :fct-ref:`insight.set_solution_database` method, or a default solution database object if none was specified.
        """

    @abstractmethod
    def set_solution_database(self, solution_database: SolutionDatabase) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Sets the value that will be returned by queries for the solution database, in test mode.

        Parameters
        ----------
        solution_database : SolutionDatabase
            The solution database information to be returned in test mode.

        Examples
        --------
        Configure a `SolutionDatabase` to be returned by future calls to `get_solution_database()`:

        >>> solution_database = xi.SolutionDatabase(host="localhost")
        >>> insight.set_solution_database(solution_database)

        Notes
        -----
        The `set_solution_database` method can only be called in test mode. Calling this method when `insight.test_mode`
        is `False` will cause the model to abort with a runtime error.

        See Also
        --------
        AppInterface.get_solution_database
        """

    @abstractmethod
    def get_resource_limits(self) -> ResourceLimits:
        #
        # noinspection PyUnresolvedReferences
        """
        Query the resource limits including the threads and memory available for use.

        Returns
        -------
        resource_limits : ResourceLimits
            The ResourceLimits object.

        Examples
        --------
        Demonstration of getting the number of threads and amount of memory available for use during execution.

        >>> resource_limits = insight.get_resource_limits()
        >>> print("Obtained threads: "+ resource_limits.threads)
        >>> if resource_limits.memory:
        >>>   print("Obtained memory:  "+ resource_limits.memory)
        """

    @abstractmethod
    def set_resource_limits(self, resource_limits: ResourceLimits) -> None:
        #
        # noinspection PyUnresolvedReferences
        """
        Sets the value that will be returned by queries for the resource limits, in test mode.

        Parameters
        ----------
        resource_limits : ResourceLimits
            The resource limits information to be returned in test mode.

        Examples
        --------
        Configure a `ResourceLimits` to be returned by future calls to `get_resource_limits()`:

        >>> resource_limits = xi.ResourceLimits(threads=1, memory=100)
        >>> insight.set_resource_limits(resource_limits)
        """

    @abstractmethod
    def populate(self,
                 entities: Union[Iterable[str], Iterable[EntityBase]] = None,
                 *,
                 entity_filter: Callable[[Entity], bool] = None,
                 fetch_individual_series: bool = False) -> None:
        """
        Reads the values of the specified entities for the current scenario into the current Insight app class.

        Parameters
        ----------
        entities : Union[Iterable[str], Iterable[EntityBase]], optional
            The entities to be populated. May be specified as a list of entity names or entity objects.
            If names are specified, columns can be identified using the pattern `"<frame_name>.<col_name>"` or by
            using their entity names (by default `"<frame_name>_<col_name>"`).
            If a DataFrame is specified, then we will populate all columns in the frame declared with either
            `manage=INPUT`.
        entity_filter : Callable[[Entity], bool], optional
            If specified, the given function will be called for each `Entity` and that entity will be populated
            if the function returned `True`.
        fetch_individual_series : bool, optional
            Configures method by which DataFrame entities are fetched from the Insight repository; when `True`, they
            are fetched as an entire frame; when `False` they are fetched as individual series and then combined into
            a DataFrame within the Python runtime. The default (`True`) is more efficient at the expense of using
            more memory in the Insight worker for some scenarios; try setting to `False` if you encounter memory
            errors in the worker when requesting a large data frame.

        Examples
        --------
        Demonstration of populating named entities

        >>> import xpressinsight as xi
        ...
        ... @xi.AppConfig("My App", partial_populate=True)
        ... class InsightApp(xi.AppBase):
        ...     @xi.ExecModeLoad()
        ...     def load(self):
        ...         self.insight.populate(['profit', 'factories_frame'])

        Demonstration of populating all entities starting 'factor'

        >>> import xpressinsight as xi
        ...
        ... @xi.AppConfig("My App", partial_populate=True)
        ... class InsightApp(xi.AppBase):
        ...     @xi.ExecModeLoad()
        ...     def load(self):
        ...         self.insight.populate(
        ...             entity_filter=lambda e: e.entity_name.startswith('factor'))

        Raises
        ------
        RuntimeError
            If called from an execution mode declared with `clear_input=True`, or an app not declared with
            `partial_populate=True`
        KeyError
            If a specified entity name cannot be found.
        TypeError
            If a specified entity is not an input entity, or is a `Param`-type entity.
        InterfaceError
            If there is some other error communicating with the Insight worker.

        Notes
        -----
        By default, execution modes without `clear_input=True` always populate all input entities. The app
        configuration must set the `partial_populate` attribute to `True` to turn off automatic population
        and allow entities to be populated through this function.

        Parameter entities are always populated by default and cannot be repopulated using this function.

        If neither `entities` nor `entity_filter` are specified, this function will populate all non-parameter
        entities with `manage=INPUT`.

        Existing values in the specified entities will be overwritten. When populating columns in a `DataFrame` or
        `PolarsDataFrame`, any existing columns in that data-frame will not be retained.

        This function may not be called more than once per execution mode.

        This function must not be called from an execution mode declared `clear_input=True`.

        This function must not be called from an app not configured with `partial_populate=True`.
        """

    @abstractmethod
    def _set_inputs_populated(self):
        """ Set flag to indicate the input entities for the given execution mode have been populated. """

    @abstractmethod
    def _reset_inputs_populated(self):
        """ Flag set to indicate the input entities for the given execution mode have not been populated. """

    @abstractmethod
    def capture(self,
                entities: Union[Iterable[str], Iterable[EntityBase]] = None,
                *,
                entity_filter: Callable[[Entity], bool] = None) -> None:
        """
        Sets the list of entities to be saved back to the Insight scenario at the end of the current execution mode.

        Parameters
        ----------
        entities : Union[Iterable[str], Iterable[EntityBase]], optional
            The entities to be captured. May be specified as a list of entity names or entity objects.
            If names are specified, columns can be identified using the pattern `"<frame_name>.<col_name>"` or by
            using their entity names (by default `"<frame_name>_<col_name>"`).
            If a DataFrame is specified, then we will capture all columns in the frame declared with either
            `manage=RESULT` or `update_after_execution=True`.
        entity_filter : Callable[[Entity], bool], optional
            If specified, the given function will be called for each `Entity` and that entity will be captured
            if the function returned `True`.

        Examples
        --------
        Demonstration of capturing named entities

        >>> import xpressinsight as xi
        ...
        ... @xi.AppConfig("My App")
        ... class InsightApp(xi.AppBase):
        ...     @xi.ExecModeLoad()
        ...     def load(self):
        ...         self.insight.capture(['profit', 'factories_frame'])

        Demonstration of capturing all entities starting 'factor'

        >>> import xpressinsight as xi
        ...
        ... @xi.AppConfig("My App")
        ... class InsightApp(xi.AppBase):
        ...     @xi.ExecModeLoad()
        ...     def load(self):
        ...         self.insight.capture(
        ...             entity_filter=lambda e: e.entity_name.startswith('factor'))

        Raises
        ------
        RuntimeError
            If called from an execution mode declared with `clear_input=True`
        KeyError
            If a specified entity name cannot be found.
        TypeError
            If a specified entity is not a result or updateable-input entity.
        InterfaceError
            If there is some other error communicating with the Insight worker.

        Notes
        -----
        If this function is not called, then the values of all result and updateable input entities will be
        captured at the end of the execution mode.

        This function cannot be called from an execution mode with `clear_input=True`; in these execution modes,
        all input entities will be captured and this behavior cannot be changed.

        When specifying an indexed entity (e.g. a `Series` or `DataFrame`), the index entities will automatically be
        captured as well.
        """

    @abstractmethod
    def submit_metric(self, json_doc: str) -> None:
        """
        Submit the given JSON document as a metric. Intended for use by FICO apps only.

        Parameters
        ----------
        json_doc : str
            JSON document describing the metric to submit.

        Raises
        ------
        ValueError
            If the metric is rejected by the Insight worker.
        """

    @abstractmethod
    def get_metrics(self) -> Iterable[str]:
        """
        Requests the list of JSON documents passed to :fct-ref:`insight.submit_metric`.

        Notes
        -----
        Only usable in test mode.

        See Also
        --------
        AppInterface.submit_metric
        """

    @abstractmethod
    def get_rest_client(self, *,
                        client_id: Optional[str] = None,
                        secret: Optional[str] = None,
                        max_retries: int = 5) -> ins.InsightRestClient:
        """
        Creates an object for communicating with the Insight server through the REST API.

        Parameters
        ----------
        client_id : str, optional
            The client ID value to use to authenticate the session with the Insight server.  If not specified
            on-premise, will be read from the system keyring entry `"ficoxpress:<insight_url>"`.
        secret : str, optional
            The secret value to use to authenticate the session with the Insight server.  If not specified
            on-premise, will be read from the system keyring entry `"ficoxpress:<insight_url>"`.  If client_id was
            specified, keyring will specifically look for an entry with that name and client_id.
        max_retries : int, optional
            The maximum number of times to attempt to retry a failed request, before giving up.

        Raises
        ------
        ValueError:
            If sufficient credentials to authenticate are not passed to this function.
        scenario.InsightAuthenticationError
            If we are unable to authenticate using the supplied credentials.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------

        Example of obtaining an `InsightRestClient` on-premise, passing the credentials as plain text:

        >>> MY_CLIENT_ID: str = '<copy client id from Insight UI to here>'
        ... MY_SECRET: str = '<copy secret from Insight UI to here>'
        ... client = self.insight.get_rest_client(
        ...     client_id=MY_CLIENT_ID, secret=MY_SECRET)

        Example of obtaining an `InsightRestClient` in DMP:

        >>> client = self.insight.get_rest_client()

        Notes
        -----

        The REST interface can be used to make queries directly to the Insight server. This allows a wider range
        of operations than is usually permitted within an Insight scenario - creating other scenarios, executing them,
        editing their data, etc. However, it's important to note that any such requests are performed separately
        from the scenario, and do not inherit any information or privileges from it. In DMP, the returned client
        will make requests as a user named `solutionclient` - you will need to add this user to any apps you want
        to access. On premise, requests are made as the user for which the supplied `client_id` and `secret` values
        were generated.

        If executing on-premise and `client_id` or `secret` are not specified, the Python "keyring" package will be
        used to read them from an entry named `"ficoxpress:<insight_url>"`. (See the documentation of
        :fct-ref:`xpressinsight.scenario.InsightRestClient` for full details.) However, it is not
        recommended that Insight apps make use of this, due to the difficulty of inserting keys into the separate
        keyrings of the users executing models within the Insight workers.

        The returned `InsightRestClient` can be used as a context manager to ensure rapid cleanup of any resources
        (HTTP sessions, etc.).

        When test mode has been activated, this function will return an object previously specified by the
        :fct-ref:`insight.set_rest_client` method. If this has not been called, it will attempt to construct
        a client instance using the Insight URL previously passed to :fct-ref:`insight.set_insight-context`. If
        this is also not available, a `RuntimeError` will be raised.

        See Also
        --------

        AppInterface.set_rest_client
        scenario.InsightRestClient
        """

    @abstractmethod
    def set_rest_client(self, client: ins.InsightRestClient) -> None:
        """
        Sets the value that will be returned by calls to :fct-ref:`get_rest_client`, in test mode.

        Parameters
        ----------
        client : ins.InsightRestClient
            `InsightRestClient` instance to be returned by future calls to :fct-ref:`get_rest_client`.

        See Also
        --------
        AppInterface.get_rest_client
        scenario.InsightRestClient
        """
