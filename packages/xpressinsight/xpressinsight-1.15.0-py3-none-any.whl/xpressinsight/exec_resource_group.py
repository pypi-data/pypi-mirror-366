"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""

from typing import Optional, Type

from .mosel import validate_raw_ident, validate_annotation_str
from .type_checking import check_instance_attribute_types

_AppBaseType = Type["AppBase"]

DEFAULT_EXEC_RESOURCE_GROUP_NAME = 'DEFAULT'
DEFAULT_INSIGHT_ENFORCED_LENGTH_DESCRIPTION = 2048


def _validate_memory_str_is_int(memory_str: str, memory_str_suffix: str):
    value_error_msg = f'The {memory_str} can only be positive numeric Gi or Mi.'
    mem_str: str = memory_str.split(memory_str_suffix)[0]
    if not mem_str.isnumeric():
        raise ValueError(value_error_msg)
    if int(mem_str) < 0:
        raise ValueError(value_error_msg)


def _validate_memory_str(memory_str: str):
    value_error_msg = f'The {memory_str} can only be positive numeric Gi or Mi.'
    if not memory_str.endswith("Gi") and not memory_str.endswith("Mi"):
        raise ValueError(value_error_msg)

    if memory_str.endswith("Gi"):
        _validate_memory_str_is_int(memory_str, "Gi")

    if memory_str.endswith("Mi"):
        _validate_memory_str_is_int(memory_str, "Mi")


def _convert_memory(memory_str: str) -> int:
    return (int(memory_str.split("Mi")[0]) * 1048576) if memory_str.endswith("Mi") \
        else (int(memory_str.split("Gi")[0]) * 1073741824)


def _validate_memory_strings(default_memory_str: str, min_memory: str):
    value_error_msg = f'The minimum memory {min_memory} cannot be greater than default {default_memory_str}'
    if _convert_memory(min_memory) > _convert_memory(default_memory_str):
        raise ValueError(value_error_msg)


class ExecResourceGroup:
    """
    Insight execution resource group. Use this to define execution resource groups for Insight execution mode.

    Examples
    --------
    Example which creates custom execution resource groups and assigns them to execution modes.

    >>> @xi.AppConfig(name='testappconfig',
    ...               exec_resource_groups=[
    ...                  xi.ExecResourceGroup(name="One_Thread_One_Gig",
    ...                                       default_threads=1,
    ...                                       default_memory="1Gi"),
    ...                  xi.ExecResourceGroup(name="Two_Threads_Two_Gig",
    ...                                       default_threads=2,
    ...                                       default_memory="2Gi"),
    ...               ])
    ... class App(xi.AppBase):
    ...     @xi.ExecMode(name="custom",
    ...                  exec_resource_group_name="Two_Threads_Two_Gig")
    ...     def custom(self):
    ...         pass
    ...
    ...     @xi.ExecModeRun(exec_resource_group_name="One_Thread_One_Gig")
    ...     def run(self):
    ...         pass
    ...
    ...     @xi.ExecModeLoad(exec_resource_group_name="One_Thread_One_Gig")
    ...     def load(self):
    ...         pass

    See Also
    --------
    ExecResourceGroup.__init__
    """
    __name: str
    __descr: str
    __min_threads: int
    __default_threads: int
    __min_memory: Optional[str]
    __default_memory: Optional[str]

    #
    def __init__(self, name: str, descr: str = "",
                 min_threads: int = 1, default_threads: int = 1,
                 min_memory: str = None, default_memory: str = None):

        """
        Constructor for the execution resource group.

        Parameters
        ----------
        name : str
            User-defined name for execution resource group. Must be a valid identifier (alphanumeric characters
            only, starting with a letter).
        descr : str
            A description of the execution resource group.
        min_threads : int
            The minimum number of threads that the model should consume when using this resource group.
            Defaults to no limit specified (value 1). For more detailed information on thread based capacity
            scheduling please see the section "Scenario execution and job scheduling" in the Insight Developer
            Guide.
        default_threads : int
            The default number of threads that the model should consume when using this resource group.
            Defaults to no limit specified (value 1). For more detailed information on thread based capacity
            scheduling please see the section "Scenario execution and job scheduling" in the Insight Developer
            Guide.
        min_memory : str
            The minimum amount of memory that the model should consume when using this resource group.
            Defaults to no limit specified. For more detailed information on memory based capacity
            scheduling please see the section "Scenario execution and job scheduling" in the Insight Developer
            Guide.
        default_memory : str
            The default amount of memory that the model should consume when using this resource group.
            Defaults to no limit specified. For more detailed information on memory based capacity
            scheduling please see the section "Scenario execution and job scheduling" in the
            Insight Developer Guide.

        See Also
        --------
        ExecResourceGroup
        """

        self.__name = name
        self.__descr = descr
        self.__min_threads = min_threads
        self.__default_threads = default_threads
        self.__min_memory = min_memory
        self.__default_memory = default_memory
        check_instance_attribute_types(self)
        validate_raw_ident(name, 'execution resource group name')
        validate_annotation_str(descr, 'execution resource group description',
                                DEFAULT_INSIGHT_ENFORCED_LENGTH_DESCRIPTION)

        if min_threads < 1 or default_threads < 1:
            raise ValueError('The number of execution resource group threads must be between 1 and 256.')

        if min_threads > 256 or default_threads > 256:
            raise ValueError('The number of execution resource group threads must be between 1 and 256.')

        if min_threads > default_threads:
            raise ValueError('The execution resource group minimum threads must not be greater than the default.')

        if default_memory:
            _validate_memory_str(default_memory)
        if min_memory:
            _validate_memory_str(min_memory)

        if default_memory and not min_memory:
            raise ValueError('The execution resource group minimum memory must also be set if default memory is set.')

        if default_memory and min_memory:
            _validate_memory_strings(default_memory, min_memory)

    @property
    def name(self) -> str:
        """ Execution resource group name. """
        return self.__name

    @property
    def descr(self) -> str:
        """ Execution resource group description. """
        return self.__descr

    @property
    def min_threads(self) -> Optional[int]:
        """ Minimum thread allocation for this execution resource group. """
        return self.__min_threads

    @property
    def default_threads(self) -> Optional[int]:
        """ Default thread allocation for this execution resource group. """
        return self.__default_threads

    @property
    def min_memory(self) -> Optional[str]:
        """ Minimum memory allocation for this execution resource group. """
        return self.__min_memory

    @property
    def default_memory(self) -> Optional[str]:
        """ Default memory allocation for this execution resource group. """
        return self.__default_memory


DEFAULT_EXEC_RESOURCE_GROUP = ExecResourceGroup(name=DEFAULT_EXEC_RESOURCE_GROUP_NAME,
                                                descr="Default resource group which specifies 1 thread and "
                                                      "no memory limit",
                                                min_threads=1, default_threads=1,
                                                min_memory=None, default_memory=None)
