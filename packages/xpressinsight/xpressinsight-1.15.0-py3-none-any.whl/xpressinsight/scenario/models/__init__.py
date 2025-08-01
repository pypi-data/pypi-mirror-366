"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.

    Defines various structures for data sent to / returned from the Insight
    5 REST API. These are not intended for direct use by an app developer.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""

#
__version__ = '1.15.0'

from .config import InsightApiBaseModel
from .attachments import Attachment, AttachmentUpdateRequest, AttachmentTag
from .apps import App, AppCreationResponse, AppModel, AppMember, ModelEntity, ModelSchema
from .auth import BearerTokenRequest, DmpIamBearerTokenRequest, DmpIamBearerTokenResponse
from .errors import ErrorResponse, ErrorDetail, InnerError, OuterError
from .folders import Folder, FolderUpdateRequest, FolderCreationRequest
from .jobs import Job, JobCreationRequest
from .pages import Page
from .portations import Upgrade, UpgradeRequest
from .references import Reference
from .scenarios import (ScenarioSummary, Scenario, ScenarioCreationRequest, ScenarioUpdateRequest,
                        EntityData, ScenarioData, ScenarioDataQuery, ArrayFilter,
                        ScenarioDataModification, EntityDelta, ArrayDelta, ArrayElement, SetDelta)
from .users import User
