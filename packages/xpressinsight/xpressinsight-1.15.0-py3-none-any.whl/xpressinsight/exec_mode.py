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

from typing import Callable, Optional, Type
import types
import sys

from .mosel import validate_raw_ident, validate_annotation_str
from .type_checking import check_instance_attribute_types
from .exec_resource_group import ExecResourceGroup

_AppBaseType = Type["AppBase"]

DEFAULT_INSIGHT_ENFORCED_LENGTH_DESCRIPTION = 2048


# noinspection PyPep8Naming
class ExecModeName(type):
    """ Standard execution mode names. """

    @property
    def LOAD(cls) -> str:
        """ LOAD """
        return "LOAD"

    @property
    def RUN(cls) -> str:
        """ RUN """
        return "RUN"

    @property
    def NONE(cls) -> str:
        """ NONE """
        return ""


class ExecMode(metaclass=ExecModeName):
    """
    Insight execution mode decorator. Use this decorator to decorate methods of an Insight application class.

    Examples
    --------
    Example which creates a custom execution mode called `CUSTOM_RUN` with a description and with
    `clear_input` set to `False` (making this similar to the built-in `RUN` execution mode).

    >>> @xi.ExecMode(name="CUSTOM_RUN",
    ...              descr="Custom run execution mode.",
    ...              clear_input=False)
    ... def my_custom_run_mode(self):
    ...     pass

    See Also
    --------
    ExecMode.__init__
    ExecModeRun
    ExecModeLoad
    AppConfig.exec_modes
    """

    __name: str
    __descr: str
    __clear_input: bool
    __preferred_service: str
    __threads: int
    __send_progress: bool
    __exec_resource_group_name: Optional[str]
    __exec_resource_group: Optional[ExecResourceGroup]

    #
    # pylint: disable-next=too-many-arguments
    def __init__(self, name: str, descr: str = "", clear_input: bool = False,
                 preferred_service: str = "", threads: int = 0, *, send_progress: bool = False,
                 exec_resource_group_name: str = None):
        """
        Constructor for the execution mode decorator for user-defined execution modes.

        Parameters
        ----------
        name : str
            User-defined execution mode name. Must be a valid identifier (alphanumeric characters
            only, starting with a letter).
        descr : str
            A description of the execution mode.
        clear_input : bool
            Whether this execution mode causes data to be loaded directly by the model, rather than
            from the Insight server. If `True`, then this execution behaves like the default load mode,
            otherwise it behaves like the default run mode.
        preferred_service : str
            Preferred service for this execution mode.
        threads : int
            The maximum number of threads that the model should consume when running in this mode.
            Defaults to no limit specified (value 0). For more detailed information on thread based capacity scheduling
            please see the section "Scenario execution and job scheduling" in the Insight Developer Guide.
            DEPRECATED - threads is deprecated, use exec_resource_group_name to associate an ExecResourceGroup.
        send_progress : bool
            Whether this execution mode can send progress during execution.
            If `True`, calling :fct-ref:`send_progress_update` will cause the values of the annotated progress entities
            to be written back to the Insight repository. If `False`, calling :fct-ref:`send_progress_update` will do
            nothing.
        exec_resource_group_name : str
            The user-defined name of an existing ExecResourceGroup.
        exec_resource_group : ExecResourceGroup
            An existing ExecResourceGroup specifying the min/default threads, min/default memory for scheduling.

        Notes
        -----
        Parameters before `send_progress` can be specified positionally for reasons of backwards compatibility, but it's
        recommended that you always use named arguments if you're specifying parameters other than `name` and `descr`.

        See Also
        --------
        ExecMode
        ExecModeRun
        ExecModeLoad
        ExecResourceGroup
        """

        self.__name = name
        self.__descr = descr
        self.__clear_input = clear_input
        self.__preferred_service = preferred_service
        self.__threads = threads
        self.__send_progress = send_progress
        self.__app_method: Optional[types.FunctionType] = None
        self.__exec_resource_group_name = exec_resource_group_name
        self.__exec_resource_group = None

        check_instance_attribute_types(self)
        validate_raw_ident(name, 'execution mode name')
        validate_annotation_str(descr, 'execution mode description', DEFAULT_INSIGHT_ENFORCED_LENGTH_DESCRIPTION)
        validate_annotation_str(preferred_service, 'execution mode preferred service')

        if name == ExecMode.LOAD and not clear_input:
            raise ValueError(f'The clear_input attribute of the {name} execution mode must be {True} '
                             f'but it is {clear_input}.')
        if name == ExecMode.RUN and clear_input:
            raise ValueError(f'The clear_input attribute of the {name} execution mode must be {False} '
                             f'but it is {clear_input}.')

        if threads < 0:
            raise ValueError('The number of execution mode threads must not be negative.')

    @property
    def name(self) -> str:
        """ Execution mode name. """
        return self.__name

    @property
    def descr(self) -> str:
        """ Execution mode description. """
        return self.__descr

    @property
    def clear_input(self) -> bool:
        """ Whether this execution mode clears inputs. """
        return self.__clear_input

    @property
    def preferred_service(self) -> str:
        """ Preferred execution service for this execution mode. """
        return self.__preferred_service

    @property
    def threads(self) -> Optional[int]:
        """ Desired thread allocation for this execution mode.
        DEPRECATED - threads is deprecated, use exec_resource_group_name to associate an ExecResourceGroup.
        """
        return self.__threads

    @property
    def send_progress(self) -> bool:
        """ Whether this execution mode sends progress updates. """
        return self.__send_progress

    @property
    def exec_resource_group_name(self) -> Optional[str]:
        """ Execution resource group name. """
        return self.__exec_resource_group_name

    @property
    def exec_resource_group(self) -> Optional[ExecResourceGroup]:
        """ Execution resource group. """
        return self.__exec_resource_group

    def _set_exec_resource_group_name(self, exec_resource_group_name: str):
        """ Execution resource group name. """
        self.__exec_resource_group_name = exec_resource_group_name

    def _set_exec_resource_group(self, exec_resource_group: ExecResourceGroup):
        """ The execution resource group for this execution mode. """
        self.__exec_resource_group = exec_resource_group

    def call(self, app: _AppBaseType) -> int:
        """ Invoke the execution mode. """
        if self.__app_method is None:
            raise TypeError('The ExecMode method is not initialized yet.')

        return self.__app_method(app)

    def __call__(self, app_method: types.FunctionType = None) -> Callable[[_AppBaseType], int]:
        """ This is the decorator function that decorates an Insight application method. """

        if not isinstance(app_method, types.FunctionType):
            raise TypeError('The ExecMode() decorator can only be used to decorate a method.')

        def exec_mode_wrapper(app: _AppBaseType) -> int:
            if not hasattr(app, 'insight'):
                raise AttributeError(f'The class {type(app).__name__} does not have the "insight" attribute. Please '
                                     f'make sure that it is a subclass of xpressinsight.AppBase and that the __init__ '
                                     f'function of {type(app).__name__} calls the __init__ function of its super '
                                     f'class.')

            #
            with app.insight._exec_mode_lock:
                if app.insight.exec_mode != '':
                    raise RuntimeError(
                        f'Cannot call the "{self.__name}" execution mode, because the "{app.insight.exec_mode}" '
                        f'execution mode is already running.' +
                        (' In test mode, "insight.exec_mode" should be the empty string before calling an execution '
                         'mode. The execution mode automatically initializes the value of "insight.exec_mode".'
                         if app.insight.test_mode else ''))

                try:
                    if self.__clear_input:
                        app.data_connector.clear_input()
                    elif app.app_cfg.partial_populate:
                        app.data_connector.load_params()
                    elif not app.app_cfg.partial_populate:
                        app.data_connector.load_input()
                        app.insight._set_inputs_populated()
                except BaseException as e:
                    print(f"ERROR: {type(app.data_connector).__name__} failed to "
                          f"{'clear' if self.__clear_input else 'load'} the input. Reason: {e.__class__}: {e}",
                          file=sys.stderr)
                    raise e

                #
                #
                result = None
                exec_mode_exception = None

                app.insight._exec_mode = self.__name

            #

            try:
                result = app_method(app)
            except BaseException as e:  # pylint: disable=broad-except
                print(f"ERROR: The {self.name} method raised an error: {e.__class__}: {e}", file=sys.stderr)
                exec_mode_exception = e  #

            with app.insight._exec_mode_lock:
                app.insight._exec_mode = ''

                if result != 0 and result is not None:
                    print(f"ERROR: The {self.name} method returned a non-zero exit code: {result}.", file=sys.stderr)

                try:
                    if self.__clear_input:
                        app.data_connector.save_input()
                    else:
                        app.data_connector.save_result()
                except BaseException as e:  # pylint: disable=broad-except
                    print(f"ERROR: {type(app.data_connector).__name__} failed to save the "
                          f"{'input' if self.__clear_input else 'result'}. Reason: {e.__class__}: {e}",
                          file=sys.stderr)
                    #
                    if exec_mode_exception is None:
                        raise e
                finally:
                    #
                    app.data_connector.reset_result_entities_to_save()
                    app.insight._reset_inputs_populated()

                #
                if exec_mode_exception is not None:
                    raise exec_mode_exception

                #
                return 0 if result is None else result

        self.__app_method = exec_mode_wrapper
        exec_mode_wrapper.exec_mode = self
        return exec_mode_wrapper


class ExecModeLoad(ExecMode):
    """
    Decorator class for the built-in `LOAD` execution mode. Use this decorator to decorate exactly one class method
    of an Insight application.

    The `ExecModeLoad` is a shortcut for `ExecMode` where `name` is set to `LOAD` and `clear_input`
    is set to `True`.

    Examples
    --------
    Example of defining a load mode.

    >>> @xi.ExecModeLoad(descr="Loads input data.")
    ... def load(self):
    ...     pass

    See Also
    --------
    ExecModeLoad.__init__
    ExecMode
    ExecModeRun
    """

    def __init__(self, descr: str = "The built-in execution mode LOAD.", preferred_service: str = "",
                 threads: int = 0, *, send_progress: bool = False, exec_resource_group_name: str = None):
        """
        Constructor for the `LOAD` execution mode decorator.

        Parameters
        ----------
        descr : str
            A description of the execution mode.
        preferred_service : str
            Preferred service for this execution mode.
        threads : int
            The maximum number of threads that the model should consume when running in this mode.
            Defaults to no limit specified (value 0). For more detailed information on thread based capacity scheduling
            please see the section "Scenario execution and job scheduling" in the Insight Developer Guide.
        send_progress : bool
            Whether this execution mode can send progress during execution.
            If `True`, calling :fct-ref:`send_progress_update` will cause the values of the annotated progress entities
            to be written back to the Insight repository. If `False`, calling :fct-ref:`send_progress_update` will do
            nothing.

        Notes
        -----
        Parameters before `send_progress` can be specified positionally for reasons of backwards compatibility, but it's
        recommended that you always use named arguments if you're specifying parameters other than `descr`.

        See Also
        --------
        ExecMode
        ExecModeLoad
        ExecModeRun
        """

        super().__init__(name="LOAD", descr=descr, clear_input=True, preferred_service=preferred_service,
                         threads=threads, send_progress=send_progress,
                         exec_resource_group_name=exec_resource_group_name)


class ExecModeRun(ExecMode):
    """
    Decorator class for the built-in `RUN` execution mode. Use this decorator to decorate exactly one class method
    of an Insight application.

    The `ExecModeRun` is a shortcut for `ExecMode` where `name` is set to `RUN` and `clear_input`
    is set to `False`.

    Examples
    --------
    Example of defining a run mode.

    >>> @xi.ExecModeRun(descr="Computes the results.")
    ... def run(self):
    ...     pass

    See Also
    --------
    ExecModeRun.__init__
    ExecMode
    ExecModeLoad
    """

    def __init__(self, descr: str = "The built-in execution mode RUN.", preferred_service: str = "",
                 threads: int = 0, *, send_progress: bool = False, exec_resource_group_name: str = None):
        """
        Constructor for the `RUN` execution mode decorator.

        Parameters
        ----------
        descr : str
            A description of the execution mode.
        preferred_service : str
            Preferred service for this execution mode.
        threads : int
            The maximum number of threads that the model should consume when running in this mode.
            Defaults to no limit specified (value 0). For more detailed information on thread based capacity scheduling
            please see the section "Scenario execution and job scheduling" in the Insight Developer Guide.
        send_progress : bool
            Whether this execution mode can send progress during execution.
            If `True`, calling :fct-ref:`send_progress_update` will cause the values of the annotated progress entities
            to be written back to the Insight repository. If `False`, calling :fct-ref:`send_progress_update` will do
            nothing.

        Notes
        -----
        Parameters before `send_progress` can be specified positionally for reasons of backwards compatibility, but it's
        recommended that you always use named arguments if you're specifying parameters other than `descr`.

        See Also
        --------
        ExecMode
        ExecModeLoad
        ExecModeRun
        """

        super().__init__(name="RUN", descr=descr, clear_input=False, preferred_service=preferred_service,
                         threads=threads, send_progress=send_progress,
                         exec_resource_group_name=exec_resource_group_name)
