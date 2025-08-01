"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Defines interface-related error classes.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2025-2025 Fair Isaac Corporation. All rights reserved.
"""

class InterfaceError(Exception):
    #
    # noinspection PyUnresolvedReferences
    """
    An exception that occurred during a call to certain `AppInterface` methods.

    Attributes
    ----------
    message : str
        The error message.

    Notes
    -----
    `InterfaceError` is only used by certain `AppInterface` functions. For each function that uses this exception,
    the documentation explicitly mentions that the function may raise an `InterfaceError`.

    `InterfaceError` defines __str__() so the error type and message can be printed directly.

    Examples
    --------

    Example of using :fct-ref:`AppInterface.get_item_info` with error handling to obtain info for the current scenario.

    >>> @xi.ExecModeLoad()
    >>> def load(self):
    >>>     try:
    >>>         info = self.insight.get_item_info(".")
    >>>         print(info)
    >>>     except xi.InterfaceError as ex:
    >>>         print(ex)  # Print error type and message.
    >>>         # print("ERROR:", ex.message)  # Print error message.

    See Also
    --------
    AppInterface.get_item_info
    AppInterface.get_item_infos
    """

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        """ Prints the error message and the cause, if the cause is not `None`. """
        msg = f"{type(self).__name__}: {self.message}"
        cause = f" Caused by {type(self.__cause__).__name__}: {self.__cause__}" \
            if self.__cause__ is not None else ""
        return msg + cause


class ScenarioNotFoundError(InterfaceError):
    """ Error raised when a requested scenario is not found in the Insight repository. """


class InvalidEntitiesError(InterfaceError):
    """
    Error raised when the requested entities are inconsistent with the schema of the Insight scenario being accessed.
    """


#
def _raise_runtime_error(message: str, cause: Exception = None):
    """ Used when Insight AppInterface is in an invalid state. """
    raise RuntimeError(message) from cause


#
def _raise_io_error(message: str, cause: Exception = None):
    """ Used when Insight AppInterface runs into an IO error. """
    #
    raise IOError(message) from cause


#
def _raise_interface_error(message: str, cause: Exception = None):
    """ Used for AppInterface functions, as an alternative to returning status codes. """
    raise InterfaceError(message) from cause
