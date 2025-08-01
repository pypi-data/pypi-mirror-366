"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    'Interface' subpackage defines interface for interacting with Insight server during execution.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""

from .interface_errors import (
    _raise_interface_error,
    _raise_runtime_error,
    _raise_io_error,
    InterfaceError,
    ScenarioNotFoundError,
    InvalidEntitiesError,
)
from .attach_errors import (
    AttachError,
    AttachNotFoundError,
    AttachFilenameInvalidError,
    AttachDescriptionInvalidError,
    AttachAlreadyExistsError,
    AttachTooLargeError,
    TooManyAttachError,
    AttachTagsInvalidError,
    SeveralAttachFoundError,
    RuntimeAttachError,
    AttachStatus,
)
from .interface import (
    Attachment,
    AttachmentRules,
    AttachTag,
    AttachTagUsage,
    AttachType,
    AppInterface,
    ItemInfo,
    Metric,
    ObjSense,
    InsightContext,
    InsightDmpContext,
    SolutionDatabase,
    ResourceLimits,
    SCENARIO_DATA_CONTAINER,
)
from .interface_rest import (
    AppRestInterface
)
from .interface_test import (
    AppTestInterface,
    XpriAttachmentsCache,
    read_attach_info,
    write_attach_info
)
