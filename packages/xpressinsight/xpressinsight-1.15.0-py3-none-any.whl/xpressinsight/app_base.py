"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2025 Fair Isaac Corporation. All rights reserved.
"""

from abc import ABC
import os
from collections import Counter
from datetime import timedelta
import types
from typing import ValuesView, List, Dict, Type, Tuple, Optional, Iterable, Callable, Union
import sys
import inspect
import threading

from .entities_config import EntitiesConfig, EntitiesContainer
from .entities import Entity, EntityBase, DataFrameBase, Manage
from .mosel import validate_raw_ident
from .type_checking import check_instance_attribute_types, validate_list, XiEnum
from .exec_mode import ExecMode, ExecModeLoad, ExecModeRun
from .exec_resource_group import ExecResourceGroup, DEFAULT_EXEC_RESOURCE_GROUP, DEFAULT_EXEC_RESOURCE_GROUP_NAME
from .interface import AppInterface, AppTestInterface, AppRestInterface
from .data_connectors import DataConnector, AppDataConnector, MoselParquetConnector, InsightWorkerParquetConnector
from .slow_tasks_monitor import SlowTasksMonitor


class AppVersion:
    # noinspection PyUnresolvedReferences
    """
        Class to represent the version number of an Insight Python app, according to semver
        (Semantic Versioning) conventions.

        Examples
        --------
        Example of specifying version "1.2.3"

        >>> import xpressinsight as xi
        ...
        ... @xi.AppConfig(name="My App", version=xi.AppVersion(1, 2, 3))
        ... class InsightApp(xi.AppBase):
        ...     pass

        See Also
        --------
        AppConfig
        AppVersion.__init__
        """

    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0):
        """
        Initializes `AppVersion` with major, minor, and patch version information.

        Parameters
        ----------
        major : int
            The major version between 0 and 999.
        minor : int
            The minor version between 0 and 999.
        patch : int
            The patch version between 0 and 999.

        See Also
        --------
        AppConfig
        AppVersion
        """

        for i in [major, minor, patch]:
            if not isinstance(i, int):
                raise TypeError('The parameters of AppVersion must be integers, '
                                f'but one parameter is a {type(i).__name__} and has value {i}.')
            if i < 0 or 999 < i:
                raise ValueError("The parameters of AppVersion must be integers between 0 and 999, "
                                 f"but one parameter value is {i}.")

        self.__major: int = major
        self.__minor: int = minor
        self.__patch: int = patch

    @property
    def major(self) -> int:
        """Major version number"""
        return self.__major

    @property
    def minor(self) -> int:
        """Minor version number"""
        return self.__minor

    @property
    def patch(self) -> int:
        """Patch version number"""
        return self.__patch

    def __str__(self):
        return f"{self.__major}.{self.__minor}.{self.__patch}"

    def __repr__(self):
        return f"AppVersion({self.__major}, {self.__minor}, {self.__patch})"


class ResultDataDelete(XiEnum):
    # noinspection PyUnresolvedReferences
    """
    When to delete scenario results data.

    Attributes
    ----------
    ON_CHANGE
        Delete scenario result data when the scenario input-data is edited, or when scenario is queued for execution.
    ON_EXECUTE
        Delete scenario result data when scenario starts to execute.
    ON_QUEUE
        Delete scenario result data when scenario is queued for execution.

    See Also
    --------
    ResultData
    """

    ON_CHANGE = "on-change"
    ON_EXECUTE = "on-execute"
    ON_QUEUE = "on-queue"


class ResultData:
    """
    Class which specifies how to handle result data within the Insight server.

    Examples
    --------
    Example showing how to configure Insight to delete the result data when the
    scenario is queued for execution.

    >>> @xi.AppConfig(name="My App",
    ...               version=xi.AppVersion(1, 0, 0),
    ...               raise_attach_exceptions=True,
    ...               result_data=xi.ResultData(
    ...                   delete=xi.ResultDataDelete.ON_QUEUE
    ...               ))
    ... class InsightApp(xi.AppBase):
    ...     pass

    See Also
    --------
    AppConfig
    ResultData.__init__
    ResultDataDelete
    """

    __delete: ResultDataDelete

    def __init__(self, delete: ResultDataDelete = ResultDataDelete.ON_CHANGE):
        """
        Initializes `ResultData` with delete strategy.

        Parameters
        ----------
        delete : ResultDataDelete
            When to delete scenario results data.
            Results data is deleted when a certain state change occurs for the scenario.
            This attribute identifies this state change as either whenever a scenario is modified,
            when it is queued, or when it begins execution.

        See Also
        --------
        AppConfig
        ResultData
        ResultDataDelete
        """

        self.__delete = delete
        check_instance_attribute_types(self)

    def __repr__(self):
        return f"ResultData(delete={repr(self.delete)})"

    @property
    def delete(self) -> ResultDataDelete:
        """ When to delete scenario results data. """
        return self.__delete


class NextAppAttributes(threading.local):
    """
    Attributes to be used by the next app to be created on this thread.
    Used by app_runner / test_runner to pass additional arguments to the AppBase constructor.
    """

    def __init__(self):
        super().__init__()
        #
        self.test_mode = True
        #
        self.work_dir = None

    def reset(self):
        """ Reset the 'next app attributes' to the default state (test mode with no work dir). """
        self.test_mode = True
        self.work_dir = None


class AppConfig(EntitiesConfig):
    # noinspection PyTypeChecker
    """
    Insight application configuration decorator. An Insight application class must be decorated with this decorator.

    Examples
    --------
    Example of a minimal Insight app showing the application configuration decorator:

    >>> import xpressinsight as xi
    ... import sys
    ...
    ... @xi.AppConfig(name="AppConfig Example",
    ...               version=xi.AppVersion(1, 0, 0),
    ...               raise_attach_exceptions=True)
    ... class InsightApp(xi.AppBase):
    ...     @xi.ExecModeLoad()
    ...     def load(self):
    ...         print(f"Current app name: {self.insight.app_name}")
    ...         print(f"Default app name: {self.app_cfg.name}")
    ...         print(f"App version:      {self.app_cfg.version}")
    ...
    ...     @xi.ExecModeRun()
    ...     def run(self):
    ...         pass
    ...
    ... if __name__ == "__main__":
    ...     app = xi.create_app(InsightApp)
    ...     app.insight.app_name = "My " + app.app_cfg.name
    ...     sys.exit(app.call_exec_mode("LOAD"))
    ...
    Current app name: My AppConfig Example
    Default app name: AppConfig Example
    App version:      1.0.0

    See Also
    --------
    AppConfig.__init__
    AppBase.app_cfg
    """
    __name: str
    __version: AppVersion
    __result_data: ResultData
    __partial_populate: bool
    __slow_task_threshold: timedelta
    __raise_attach_exceptions: Optional[bool]
    __allow_duplicate_indices: Optional[bool]
    _next_app_attrs: NextAppAttributes

    def __init__(self,
                 name: str,
                 version: AppVersion = AppVersion(0, 0, 0),
                 result_data: ResultData = ResultData(),
                 scen_types: List[str] = None,
                 exec_resource_groups: List[ExecResourceGroup] = None,
                 partial_populate: bool = False,
                 slow_task_threshold: timedelta = timedelta(minutes=2),
                 raise_attach_exceptions: Optional[bool] = None,
                 allow_duplicate_indices: Optional[bool] = None):
        """
        Insight AppConfig constructor. Use this decorator to decorate the Insight application class.

        Parameters
        ----------
        name : str
            Name of the Insight application.
        version : AppVersion, default AppVersion(0, 0, 0)
            Version of the Insight application.
        result_data : ResultData, default ResultData()
            Configuration for result data handling.
        scen_types : List[str], optional
            List of scenario type identifiers. It is not necessary to declare the standard
            `"SCENARIO"` type as all apps have this type.
        partial_populate : bool, default False
            Whether to skip populating the input entities before the start of the execution mode.
            If `True`, only `Param`-type entities will be populated automatically; the execution mode must call
            :fct-ref:`insight.populate` to populate any other entities required.
        slow_task_threshold : timedelta, default 2 minutes
            Internal tasks taking this time or longer will result in warnings output to the run log.
            This is a troubleshooting setting that can be used to track if internal xpressinsight operations
            are being unexpectedly time-consuming.
        raise_attach_exceptions : bool, optional
            Whether errors during attachment operations should be raised as exceptions (`True`). If `False` or
            unset, the app developer must check the `attach_status` property of `AppInterface` after every attachment
            operation to check if it succeeded.
        allow_duplicate_indices : bool, optional
            Whether to skip the check for duplicate index tuples in `Series` / `DataFrame` / `PolarsDataFrame` entities,
            and duplicate values in `Index` / `PolarsIndex` entities. If `False`, an error will be raised
            at the end of the execution mode if you have added any duplicate values to entities. If set to `True`,
            no error will be raised, and duplicates will be silently removed as data is saved back to Insight.
            If `None` (the current default), a warning will be output when duplicates are detected. The default value of
            this parameter will be changed to `False` from xpressinsight version 1.16.

        See Also
        --------
        AppConfig
        AppBase.app_cfg
        """
        super().__init__()
        self.__exec_modes: Dict[str, ExecMode] = {}
        self.__exec_resource_groups: Dict[str, ExecResourceGroup] = {}

        if exec_resource_groups:
            self.__exec_resource_groups = {x.name: x for x in
                                           validate_list(None,
                                                         'exec_resource_groups',
                                                         ExecResourceGroup,
                                                         'xpressinsight.ExecResourceGroup',
                                                         exec_resource_groups)}

        self.__name = name
        self.__version = version
        self.__result_data = result_data
        self.__scen_types: Tuple[str, ...] = self.__validate_scen_types(scen_types)
        self.__partial_populate = partial_populate
        self.__slow_task_threshold = slow_task_threshold
        self.__allow_duplicate_indices = allow_duplicate_indices
        self.__raise_attach_exceptions = raise_attach_exceptions
        self.__data_connector_cls: Type[DataConnector] = MoselParquetConnector
        self.__insight_worker_data_connector_cls: Type[DataConnector] = InsightWorkerParquetConnector
        #
        #
        #
        self._next_app_attrs = NextAppAttributes()
        check_instance_attribute_types(self)

    def __validate_scen_types(self, scen_types: Optional[List[str]]) -> Tuple[str, ...]:
        default_scen_type = 'SCENARIO'

        if scen_types is None:
            return (default_scen_type,)

        scen_types = validate_list(self, 'scen_types', str, 'string', scen_types)
        scen_types_set = set(scen_types)

        if len(scen_types_set) < len(scen_types):
            raise ValueError("All scenario type identifiers must be unique.")

        for scen_type in scen_types:
            validate_raw_ident(scen_type, 'scenario type identifier')

        reserved = {'FOLDER', 'VIRTUAL'}.intersection(scen_types_set)
        if len(reserved) > 0:
            raise ValueError(
                f'"{reserved.pop()}" is not a valid scenario type identifier, because it is a reserved keyword.')

        if default_scen_type in scen_types_set:
            return scen_types

        return (default_scen_type,) + scen_types

    @property
    def name(self) -> str:
        """
        Get the default name of the app.

        Returns
        -------
        name : str
            The default name of the app.

        Notes
        -----
        This property returns the default app name. Use the Insight app interface to get the current app name:
        :fct-ref:`insight.app_name`.

        See Also
        --------
        AppConfig
        AppInterface.app_name
        """
        return self.__name

    @property
    def version(self) -> AppVersion:
        """
        Get the version number of the app.

        Returns
        -------
        version : AppVersion
            The version number of the app.

        See Also
        --------
        AppConfig
        AppVersion
        """
        return self.__version

    @property
    def result_data(self) -> ResultData:
        """
        Get the result data configuration of the app.

        Returns
        -------
        result_data : ResultData
            The result data configuration of the app.

        See Also
        --------
        AppConfig
        ResultData
        """
        return self.__result_data

    @property
    def scen_types(self) -> Tuple[str, ...]:
        """
        Get the scenario types of the app.

        Returns
        -------
        scen_types : Tuple[str, ...]
            The scenario types of the app.

        See Also
        --------
        AppConfig
        """
        return self.__scen_types

    @property
    def partial_populate(self) -> bool:
        """
        Whether this app is using the 'partial populate' pattern.

        Returns
        -------
        partial_populate : bool
            `True` if this is a partial-populate app, `False` if the execution modes automatically populate the
            input entities.

        See Also
        --------
        AppConfig
        """
        return self.__partial_populate

    @property
    def allow_duplicate_indices(self) -> Optional[bool]:
        """
        Whether to skip the check for duplicate index tuples in `Series` / `DataFrame` / `PolarsDataFrame` entities,
        and duplicate values in `Index` / `PolarsIndex` entities. If `False` (the default), an error will be raised
        at the end of the execution mode if you have added any duplicate values to entities. If set to `True`,
        no error will be raised, and duplicates will be silently removed as data is saved back to Insight.
        If `None` (the default), a warning will be output when duplicates are detected; the default value of
        this attribute will be changed to `False` from xpressinsight version 1.16.

        Returns
        -------
        allow_duplicate_indices : bool, optional
            `False` to error when duplicate indices are encountered, `True` to silently ignore them, `None` to
            log out a warning.

        See Also
        --------
        AppConfig
        """
        return self.__allow_duplicate_indices

    @property
    def slow_task_threshold(self) -> timedelta:
        """
        When internal tasks taking longer than this threshold, warnings will be written to the run log.

        Returns
        -------
        slow_task_threshold : timedelta
            Minimum elapsed time for a task to be considered 'slow'.

        See Also
        --------
        AppConfig
        """
        return self.__slow_task_threshold

    @property
    def raise_attach_exceptions(self) -> bool:
        """
        Property indicating whether to raise an exception on an attachment-related error (such as attempting
        to get an attachment that doesn't exist, or put an attachment too large to be accepted by Insight).

        Notes
        -----
        When set to `False` or `None`, the caller must check the `attach_status` property of the `AppInterface` after
        every attachment operation to detect errors.

        See Also
        --------
        AppConfig.__init__
        AppInterface.attach_status
        AppInterface.raise_attach_exceptions
        """
        return self.__raise_attach_exceptions

    @property
    def _data_connector_cls(self) -> Type[DataConnector]:
        """ Property for the type of the data connector. For FICO internal use only. """
        return self.__data_connector_cls

    @property
    def _insight_worker_data_connector_cls(self) -> Type[DataConnector]:
        """ Property for the type of the data connector for communicating with the Insight worker. For FICO internal
            use only. """
        return self.__insight_worker_data_connector_cls

    @_insight_worker_data_connector_cls.setter
    def _insight_worker_data_connector_cls(self, value: Type[DataConnector]) -> None:
        """ Set the type of the data connector for communicating with the Insight worker. For FICO internal use
            only. """
        self.__insight_worker_data_connector_cls = value

    @staticmethod
    def __get_exec_modes(app_cls):
        exec_modes = {}

        for attr_name, attr in inspect.getmembers(app_cls):
            if hasattr(attr, 'exec_mode') and isinstance(attr.exec_mode, ExecMode):
                if isinstance(attr, types.FunctionType):
                    if exec_modes.get(attr.exec_mode.name) is not None:
                        raise KeyError(f'The {attr.exec_mode.name} execution mode cannot be defined twice.')

                    exec_modes[attr.exec_mode.name] = attr.exec_mode
                else:
                    raise TypeError('The ExecMode() decorator can only be used to decorate a method. ' +
                                    f'The attribute "{attr_name}" is not a method.')

        for mode_name, mode_cls in {ExecMode.LOAD: ExecModeLoad, ExecMode.RUN: ExecModeRun}.items():
            if mode_name not in exec_modes:
                print(f'WARNING: Class {app_cls.__name__} does not define a {mode_name} execution mode. It is '
                      f'necessary to decorate a method with the @{mode_cls.__name__}() decorator. If a method is '
                      f'already decorated with this decorator, then check whether the function has a unique name.',
                      file=sys.stderr)

        return exec_modes

    @property
    def exec_modes(self) -> ValuesView[ExecMode]:
        """
        Get the list of all execution modes of the app.

        Returns
        -------
        exec_modes : ValuesView[ExecMode]
            The execution modes of the app.

        See Also
        --------
        AppConfig.get_exec_mode
        AppConfig
        ExecMode
        """
        return self.__exec_modes.values()

    def get_exec_mode(self, name: str) -> Optional[ExecMode]:
        """
        Get an execution mode object by name.

        Parameters
        ----------
        name : str
            The name of the execution mode.

        Returns
        -------
        exec_mode : Optional[ExecMode]
            The execution mode object or `None` if not found.

        See Also
        --------
        AppConfig.exec_modes
        AppConfig
        ExecMode
        """
        return self.__exec_modes.get(name)

    @property
    def exec_resource_groups(self) -> ValuesView[ExecResourceGroup]:
        """
            Get the list of all execution resource groups of the app.

            Returns
            -------
            exec_modes : ValuesView[ExecResourceGroup]
                The execution resource groups of the app.

            """
        return self.__exec_resource_groups.values()

    def get_exec_resource_group(self, name: str) -> Optional[ExecResourceGroup]:
        """
        Get an execution resource group of the app.

        Returns
        -------
        exec_resource_group : Optional[ExecResourceGroup]
            The execution resource group of the app associated with a name.

        """

        return self.__exec_resource_groups[name]

    def __get_insight_entity_names(self) -> List[str]:
        """ Get the names that the entities will have in the Insight schema (ie Entity.entity_name) - for
            composed entities like DataFrame, includes the entity names of the columns. """
        entity_names: List[str] = []
        for entity in self.entities:
            if isinstance(entity, Entity):
                entity_names.append(entity.entity_name)
            elif isinstance(entity, DataFrameBase):
                for col in entity.columns:
                    entity_names.append(col.entity_name)
            else:
                raise TypeError(f"Unrecognized entity type {type(entity)}")

        return entity_names

    def __check_entity_names_unique(self) -> None:
        """ Check that none of the entity_names are duplicates. Raise error if so. """
        all_entity_names = self.__get_insight_entity_names()
        duplicate_entity_names = [name for name, count in Counter(all_entity_names).items() if count > 1]
        if duplicate_entity_names:
            raise TypeError(f'Duplicate entity name "{duplicate_entity_names[0]}".')

    def __check_attribute_names_valid(self) -> None:
        """ Check that the attribute names of all entities are all valid to be attributes of an app class.
            Raise error if not. """
        app_base_names = {member[0] for member in inspect.getmembers(AppBase)}
        for entity in self.entities:
            if entity.name in app_base_names:
                raise ValueError(f"Invalid name '{entity.name}' for entity. Must not be a reserved keyword.")

    def __set_default_group_name_to_execution_modes_if_threads_absent(self) -> None:
        #
        #
        threads_defined = any(x.threads > 0 for x in self.__exec_modes.values())
        if not threads_defined:
            for exec_mode in self.__exec_modes.values():
                if not exec_mode.exec_resource_group_name and exec_mode.name in ["LOAD", "RUN"]:
                    exec_mode._set_exec_resource_group_name(DEFAULT_EXEC_RESOURCE_GROUP_NAME)

    def __add_execution_groups_to_execution_modes(self) -> None:

        self.__set_default_group_name_to_execution_modes_if_threads_absent()
        #
        #
        exec_mode_used_groups = set()
        for exec_mode in self.__exec_modes.values():
            if exec_mode.threads > 0 and exec_mode.exec_resource_group_name:
                raise ValueError(f'The execution mode {exec_mode.name} cannot '
                                 f'define both threads and a resource group.')

            if exec_mode.exec_resource_group_name:
                if exec_mode.exec_resource_group_name == "DEFAULT":
                    exec_mode._set_exec_resource_group(DEFAULT_EXEC_RESOURCE_GROUP)
                else:
                    if not self.__exec_resource_groups.__contains__(exec_mode.exec_resource_group_name):
                        raise KeyError(f'The {exec_mode.exec_resource_group_name} '
                                       f'execution resource group does not exist.')
                    exec_mode._set_exec_resource_group(
                        self.__exec_resource_groups[exec_mode.exec_resource_group_name])
                    exec_mode_used_groups.add(exec_mode.exec_resource_group_name)

        exec_mode_groups_not_used = [x for x in self.__exec_resource_groups.keys() if x not in exec_mode_used_groups]
        if len(exec_mode_groups_not_used) > 0:
            raise ValueError(f'The resource groups {exec_mode_groups_not_used} are not used.')

    def __call__(self, app_cls=None):
        if not issubclass(app_cls, AppBase):
            raise TypeError(f'The Insight app {app_cls.__name__} must be a subclass of xpressinsight.AppBase.')

        self.__exec_modes = self.__get_exec_modes(app_cls)
        self.__add_execution_groups_to_execution_modes()

        entities_map = self._init_entities(app_cls, recommended_annotation_prefix="xi.types", allow_old_syntax=True)

        for entity in self.entities:
            # noinspection PyProtectedMember
            entity._init_app_entity(entities_map)

        #
        self.__check_attribute_names_valid()

        #
        self.__check_entity_names_unique()

        #
        for entity in self.entities:
            # noinspection PyProtectedMember
            entity._check_valid_app_entity()

        #
        return app_cls


class AppBase(ABC, EntitiesContainer):
    """
    The `AppBase` class. An Insight application must be a subclass of `AppBase`.

    Examples
    --------

    >>> import xpressinsight as xi
    ...
    ... @xi.AppConfig("My App")
    ... class MyApp(xi.AppBase):
    ...     pass
    """

    #
    __data_connector: Optional[AppDataConnector]
    __insight: Optional[AppInterface]
    __test_mode: bool
    __work_dir: str

    @classmethod
    def get_app_cfg(cls) -> AppConfig:
        """
        Gets the application configuration object of the Insight app.
        This class method is equivalent to the instance property `AppBase.app_cfg`.

        Returns
        -------
        app_cfg : AppConfig
            The application configuration object.

        See Also
        --------
        AppBase.app_cfg
        """
        try:
            app_cfg = cls.get_entities_cfg()
        except AttributeError as e:
            #
            raise AttributeError(
                "Cannot access the application configuration!\n"
                "    Please make sure that the Insight application class is decorated with the AppConfig decorator.\n"
                "    Please access the application configuration through self.app_cfg, where self is an instance\n"
                "    of the Insight application.") from e

        if not isinstance(app_cfg, AppConfig):
            #
            raise AttributeError(
                f"Application configuration has wrong type (expected AppConfig, found {type(app_cfg).__name__});\n"
                f"please consult FICO product support for assistance.")

        return app_cfg

    def __new__(cls, *args, **kwargs):
        if cls is AppBase:
            raise TypeError(f"Only children of {cls.__name__} may be instantiated.\n"
                            f"   Correct:  class InsightApp(xi.AppBase): ...\n"
                            f"   Wrong:    class InsightApp(xi.AppBase()): ...")

        # noinspection PyArgumentList
        return object.__new__(cls, *args, **kwargs)

    def __init__(self):
        """ Initialization function of the base class of an Insight application. """
        # noinspection PyProtectedMember
        self.__test_mode = self.app_cfg._next_app_attrs.test_mode
        # noinspection PyProtectedMember
        self.__work_dir = self.app_cfg._next_app_attrs.work_dir
        if self.__work_dir is None:
            self.__work_dir = os.path.join("work_dir", "xpressinsight")

        self.__slow_tasks_monitor = SlowTasksMonitor(warning_threshold=self.app_cfg.slow_task_threshold)

        #
        if self.__test_mode:
            app_interface_class = AppTestInterface
            app_interface_args = []
        else:
            app_interface_class = AppRestInterface
            #
            rest_port = 8083
            rest_token = "TOKEN_ABC"
            app_interface_args = [rest_port, rest_token]

        self.__insight = app_interface_class(*app_interface_args, work_dir=self.__work_dir, app=self,
                                              slow_tasks_monitor=self.__slow_tasks_monitor,
                                              raise_attach_exceptions=self.app_cfg.raise_attach_exceptions)

        #
        # noinspection PyProtectedMember
        self.__data_connector = AppDataConnector(self, self.app_cfg._data_connector_cls(self),
                                                 slow_tasks_monitor=self.__slow_tasks_monitor)

    @property
    def app_cfg(self) -> AppConfig:
        """
        Property for the application configuration object of the Insight app.

        Returns
        -------
        app_cfg : AppConfig
            The application configuration object.

        Examples
        --------
        Demonstration of using the application configuration for getting the application version number:

        >>> import xpressinsight as xi
        ...
        ... @xi.AppConfig("My App", version=xi.AppVersion(1, 0, 0))
        ... class InsightApp(xi.AppBase):
        ...     @xi.ExecModeLoad()
        ...     def load(self):
        ...         print(f"Version number: {self.app_cfg.version}")

        See Also
        --------
        AppConfig
        AppConfig.__init__
        """
        return self.__class__.get_app_cfg()

    @property
    def data_connector(self) -> AppDataConnector:
        """ Data connector being used to load / save the app's entities. """
        return self.__data_connector

    @property
    def insight(self) -> AppInterface:
        """
        Property for the application interface of the Insight app.

        Returns
        -------
        insight : AppInterface
            The application interface.

        Examples
        --------
        Demonstration of using the application interface for getting the current scenario name:

        >>> import xpressinsight as xi
        ...
        ... @xi.AppConfig("My App")
        ... class InsightApp(xi.AppBase):
        ...     @xi.ExecModeLoad()
        ...     def load(self):
        ...         print(f"Scenario name: {self.insight.scenario_name}")

        See Also
        --------
        AppInterface
        """
        return self.__insight

    @property
    def _slow_tasks_monitor(self) -> SlowTasksMonitor:
        return self.__slow_tasks_monitor

    def call_exec_mode(self, name: str) -> int:
        """ Invoke the named execution mode. """
        exec_mode = self.app_cfg.get_exec_mode(name)

        if exec_mode is None:
            print(f'ERROR: The {self.__class__.__name__} class does not have the {name} execution mode.',
                  file=sys.stderr)
            return 1

        return exec_mode.call(self)

    def call_exec_modes(self, exec_modes: List[str]) -> int:
        """ Invoke the named execution modes, in the order given. """
        for exec_mode in exec_modes:
            result = self.call_exec_mode(exec_mode)

            if result != 0:
                print(f'ERROR: The {exec_mode} execution mode failed. Exit code: {result}.',
                      file=sys.stderr)
                return result

        return 0

    def initialize_entities(self,
                            entities: Union[Iterable[str], Iterable[EntityBase]] = None,
                            *,
                            manage: Manage = None,
                            entity_filter: Callable[[Entity], bool] = None,
                            overwrite: bool = False) -> None:
        # noinspection PyUnresolvedReferences
        """
        Initialize entities to their default values (empty string, `0`, empty series or dataframe column, etc.).
        You can use arguments to specify the entities to be initialized; if no arguments are given, all the
        entities in the app will be initialized.

        When initializing some columns of a data-frame, any other columns already in the data-frame will be
        retained, as will the data-frame index. The newly added columns will be filled in with the default value
        for the column entity.

        Parameters
        ----------
        entities : Union[Iterable[str], Iterable[EntityBase]], optional
            The entities to be initialized. May be specified as a list of entity names or entity objects.
            If names are specified, columns can be identified using the pattern `"<frame_name>.<col_name>"` or by
            using their entity names (by default `"<frame_name>_<col_name>"`).
            If a DataFrame is specified, that is assumed to include all columns in the frame that have the
            requested `manage` attribute (if any were specified).
        manage : Manage, optional
            The manage-type of entities to be initialized.
        entity_filter : Callable[[Entity], bool], optional
            If specified, the given function will be called for each `Entity` and that entity will be initialized
            if the function returned `True`.
        overwrite : bool, default False
            Flag indicating whether we should overwrite existing values.
            If not set to `True` and one of the selected entities has a value, a `ValueError` will be raised rather
            than overwriting the existing value.

        Examples
        --------
        Demonstration of initializing all input entities in the model:

        >>> import xpressinsight as xi
        ...
        ... @xi.AppConfig("My App")
        ... class InsightApp(xi.AppBase):
        ...     @xi.ExecModeLoad()
        ...     def load(self):
        ...         self.initialize_entities(manage=xi.Manage.INPUT)

        Demonstration of initializing named entities:

        >>> import xpressinsight as xi
        ...
        ... @xi.AppConfig("My App")
        ... class InsightApp(xi.AppBase):
        ...     @xi.ExecModeLoad()
        ...     def load(self):
        ...         self.initialize_entities(['SalePrices', 'History'])

        Demonstration of initializing all progress entities in the model, overwriting existing values:

        >>> import xpressinsight as xi
        ...
        ... @xi.AppConfig("My App")
        ... class InsightApp(xi.AppBase):
        ...     @xi.ExecModeLoad()
        ...     def load(self):
        ...         self.initialize_entities(entity_filter=lambda e: e.update_progress,
        ...                                  overwrite=True)
        """
        #
        if entities is not None:
            if not isinstance(entities, Iterable):
                raise TypeError('"entities" must be a list of strings or Entities.')
            if not all(isinstance(e, str) for e in entities) and not all(isinstance(e, EntityBase) for e in entities):
                raise TypeError('"entities" must be a list of strings or Entities.')

        #
        if manage is not None and not isinstance(manage, Manage):
            raise TypeError('"manage" must be xi.Manage.INPUT or xi.Manage.RESULT.')
        if entity_filter is not None and not isinstance(entity_filter, Callable):
            raise TypeError('"entity_filter" must be a function.')
        if not isinstance(overwrite, bool):
            raise TypeError('"overwrite" must be a boolean.')

        #
        self.data_connector.initialize_entities(entities=entities, manage=manage,
                                                entity_filter=entity_filter, overwrite=overwrite)

    def load_and_run(self, delete_work_dir: bool = True) -> int:
        """ Invoke the LOAD execution mode, then the RUN execution mode. """
        if delete_work_dir:
            self.insight.delete_work_dir()

        return self.call_exec_modes([ExecMode.LOAD, ExecMode.RUN])
