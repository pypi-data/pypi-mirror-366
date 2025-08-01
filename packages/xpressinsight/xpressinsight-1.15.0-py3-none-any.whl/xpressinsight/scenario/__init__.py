"""
    Xpress Insight Python package
    =============================

    The 'xpressinsight.scenario' Python package can be used to call the
    Insight 5 REST API from both Python apps within Xpress Insight, and
    from independent Python scripts.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""

#
__version__ = '1.15.0'

from .apps import App, AppCreationResponse, AppMember, AppUpgradeResponse
from .attachments import Attachment, AttachmentTag, AttachmentUpdate
from .auth import BearerToken
from .common import Reference, ShareStatus, ObjectType
from .errors import (InsightServerError, InsightServerResponseError, AuthorizationError,
                     AuthenticationError, ItemNotFoundError, ScenarioTimeOutError)
from .folders import Folder
from .rest_client import InsightRestClient
from .scenarios import ModelStatus, ProblemStatus, ScenarioDataState, ScenarioSummary, Scenario
from .scenarios_data import EntityUpdate, ScalarUpdate, IndexUpdate, ArrayUpdate
from .users import User, UserStatus
