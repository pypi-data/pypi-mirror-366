"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Defines attachment-related error codes.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2025-2025 Fair Isaac Corporation. All rights reserved.
"""

from abc import ABC

from ..type_checking import XiEnum
from .interface_errors import InterfaceError


class AttachStatus(XiEnum):
    """
    Indicates the status of the most recent attempt to access or modify an attachment.

    Attributes
    ----------
    OK : int
        The operation completed successfully.
    NOT_FOUND : int
        The specified attachment does not exist.
    INVALID_FILENAME : int
        An attachment could not be created or renamed because the specified filename is invalid. It may be too long,
        too short, or contain invalid characters.
    INVALID_DESCRIPTION : int
        The specified description is invalid. The description can be a maximum of 2500 characters in length.
    ALREADY_EXISTS : int
        An attachment could not be created because another attachment with the same name already exists.
    TOO_LARGE : int
        An attachment could not be created because the attached file is too large. Attachments can be a maximum of
        150Mb in size.
    TOO_MANY : int
        An attachment could not be created because the maximum number of attachments (250) has been reached for the app
        or scenario.
    INVALID_TAGS : int
        Invalid tags were provided.
    SEVERAL_FOUND : int
        Several attachments match the given tag, but the function called only allows for one to be retrieved.

    Notes
    -----
    To maintain backwards compatibility, attachment operations will only raise exceptions on error if the
    `raise_attach_exceptions` attribute of either the `AppConfig` or `AppInterface` class is set to `True`.
    When this is not the case, after every call to an attachment-related function or procedure, you should
    check the value of `insight.attach_status` to see if your request succeeded.

    See Also
    --------
    AppConfig.raise_attach_exceptions
    AppInterface.attach_status
    AppInterface.raise_attach_exceptions
    """

    OK = 0
    NOT_FOUND = 1
    INVALID_FILENAME = 2
    INVALID_DESCRIPTION = 3
    ALREADY_EXISTS = 4
    TOO_LARGE = 5
    TOO_MANY = 6
    INVALID_TAGS = 7
    SEVERAL_FOUND = 8
    IN_PROGRESS = 254
    RUNTIME_ERROR = 255


class AttachError(InterfaceError, ABC):
    """
    Superclass for different attachment error types.
    """
    def __init__(self, message: str, attach_status: AttachStatus):
        super().__init__(message)
        self.__attach_status = attach_status

    @property
    def attach_status(self) -> AttachStatus:
        """ The status flag for this exception. """
        return self.__attach_status


class AttachNotFoundError(AttachError):
    """
    Exception raised when a requested attachment is not found.
    """
    def __init__(self, message: str):
        super().__init__(message, AttachStatus.NOT_FOUND)


class AttachFilenameInvalidError(AttachError):
    """
    Exception raised when an attachment filename is invalid.
    """
    def __init__(self, message: str):
        super().__init__(message, AttachStatus.INVALID_FILENAME)


class AttachDescriptionInvalidError(AttachError):
    """
    Exception raised when an attachment description is invalid.
    """
    def __init__(self, message: str):
        super().__init__(message, AttachStatus.INVALID_DESCRIPTION)


class AttachAlreadyExistsError(AttachError):
    """
    Exception raised when trying to add an attachment that already exists.
    """
    def __init__(self, message: str):
        super().__init__(message, AttachStatus.ALREADY_EXISTS)


class AttachTooLargeError(AttachError):
    """
    Exception raised when a file is too large to be added as an attachment.
    """
    def __init__(self, message: str):
        super().__init__(message, AttachStatus.TOO_LARGE)


class TooManyAttachError(AttachError):
    """
    Exception raised when a scenario has too many attachments to add another.
    """
    def __init__(self, message: str):
        super().__init__(message, AttachStatus.TOO_MANY)


class AttachTagsInvalidError(AttachError):
    """
    Exception raised when attachment tags are invalid.
    """
    def __init__(self, message: str):
        super().__init__(message, AttachStatus.INVALID_TAGS)


class SeveralAttachFoundError(AttachError):
    """
    Exception raised when a single attachment was requested but multiple were found.
    """
    def __init__(self, message: str):
        super().__init__(message, AttachStatus.SEVERAL_FOUND)


class RuntimeAttachError(AttachError):
    """
    Exception raised when an unexpected error occurs when performing an attachment operation.
    """
    def __init__(self, message: str):
        super().__init__(message, AttachStatus.RUNTIME_ERROR)
