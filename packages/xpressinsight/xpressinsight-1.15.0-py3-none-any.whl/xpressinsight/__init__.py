"""
    Xpress Insight Python package
    =============================

    The 'xpressinsight' Python package can be used to develop Python based web
    applications for Xpress Insight.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2025 Fair Isaac Corporation. All rights reserved.
"""

#
__version__ = '1.15.0'

from xpressinsight import types, data

from .exec_mode import ExecMode, ExecModeRun, ExecModeLoad
from .exec_resource_group import ExecResourceGroup
from .entities import (
    BasicType, boolean, integer, string, real,
    Manage, Hidden,
    Entity, EntityBase,
    Scalar, Param, IndexBase, Index, Series, DataFrameBase, DataFrame, Column,
    PolarsIndex, PolarsDataFrame,
)
from .entities_config import ScenarioData, EntitiesConfig, EntitiesContainer
from .app_base import AppVersion, AppConfig, AppBase, ResultData, ResultDataDelete
from .interface import (
    Attachment,
    AttachmentRules,
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
    AttachTag,
    AttachTagUsage,
    AppInterface,
    ItemInfo,
    ObjSense,
    Metric,
    InsightContext,
    InsightDmpContext,
    SolutionDatabase,
    ResourceLimits,
    InterfaceError,
    ScenarioNotFoundError,
    InvalidEntitiesError,
    read_attach_info,
    write_attach_info,
)
from .repository_path import RepositoryPath
from .test_runner import create_app
