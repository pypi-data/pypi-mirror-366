"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.
    Defines job-related structures returned by the Insight 5 REST API.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from typing import Optional

from .config import InsightApiBaseModel
from .references import Reference


class Job(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Jobs.html?scroll=_components_schemas_Job """
    id: str
    scenario: Optional[Reference] = None
    status: str

    def is_finished(self) -> bool:
        """ Checks whether the execution status indicates this job has finished """
        return self.status in {'COMPLETED', 'FAILED', 'DELETED', 'CANCELLED'}


class JobCreationRequest(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Jobs.html?scroll=_components_schemas_JobCreationRequest """
    scenario: Reference
    execution_mode: str
