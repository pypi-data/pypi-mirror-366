"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.
    Defines auth-related structures returned by the Insight 5 REST API
    and DMP IAM API

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from .config import InsightApiBaseModel


class BearerTokenRequest(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/rest_api/tag-Authentication.html?scroll=_components_schemas_BearerTokenRequest """
    client_id: str
    secret: str
    max_age: int


class DmpIamBearerTokenRequest(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://console.dms.int.usw2.ficoanalyticcloud.com/help/decisionmanagementplatform_3.30a/GUID-81FC1F76-6FAA-44A1-AF20-584CB72BCA86.html """
    client_id: str
    secret: str


class DmpIamBearerTokenResponse(InsightApiBaseModel):
    # pylint: disable-next=line-too-long
    """ See https://console.dms.int.usw2.ficoanalyticcloud.com/help/decisionmanagementplatform_3.30a/GUID-81FC1F76-6FAA-44A1-AF20-584CB72BCA86.html """
    #
    expiry_timestamp: int
    token_type: str
    access_token: str
