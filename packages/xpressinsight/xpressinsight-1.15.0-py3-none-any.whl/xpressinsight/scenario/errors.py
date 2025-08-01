"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from typing import Optional

import requests
from pydantic import ValidationError

from xpressinsight.scenario.models.errors import ErrorResponse
from xpressinsight.scenario.rest_client_base import is_json_content_type, is_text_content_type


class InsightServerError(RuntimeError):
    """
    Error raised when there's a problem with a request to the Insight server.
    This may be an issue communicating with the server, or an error response returned
    by the server.

    There are several subclasses that are moved for more specific use cases.
    """


class InsightServerCommunicationError(InsightServerError):
    """
    Error raised when there's an error communicating with the Insight server, e.g.
    if the Insight server is offline.
    """


class InsightServerResponseError(InsightServerError):
    """
    Error raised when the response from the Insight server cannot be understood.
    """


class ItemNotFoundError(InsightServerError):
    """
    Error raised when the Insight server responds that the requested item could not be found.
    """


class AuthenticationError(InsightServerError):
    """
    Error raised when we're unable to authenticate with the Insight server; for example, when
    the supplied `client_id` and `secret` values are not correct.
    """


class AuthorizationError(InsightServerError):
    """
    Error raised when our credentials are unable to authorize a request to the Insight server;
    for example, if we're creating an app but the user account doesn't have sufficient privileges
    to do this.
    """


class ScenarioTimeOutError(RuntimeError):
    """
    Error raised when a scenario execution did not complete within a given timeout
    """


def get_error_description(resp: requests.Response) -> Optional[str]:
    """ Return an appropriate error description string from the response. """
    if 'Content-Type' in resp.headers and is_json_content_type(resp.headers['Content-Type']):
        try:
            json = ErrorResponse.model_validate_json(resp.text)
            return json.get_error_description()
        except (ValidationError, ValueError):
            #
            return resp.text

    if 'Content-Type' in resp.headers and is_text_content_type(resp.headers['Content-Type']):
        return resp.text

    return None


def make_insight_server_error(resp: requests.Response) -> InsightServerError:
    """ Return an appropriate error to raise, given information in this response from the server. """
    err_descr = get_error_description(resp)

    if err_descr is None:
        err_msg = f"Insight server returned status code {resp.status_code} from endpoint '{resp.request.url}'"
    else:
        err_msg = (f"Insight server returned error '{err_descr}' (status code {resp.status_code}) from "
                   f"endpoint '{resp.request.url}'")

    if resp.status_code == 401:
        return AuthenticationError(err_msg)

    if resp.status_code == 403:
        return AuthorizationError(err_msg)

    if resp.status_code == 404:
        return ItemNotFoundError(err_msg)

    return InsightServerError(err_msg)


def make_unexpected_content_type_error(resp: requests.Response) -> InsightServerResponseError:
    """ Return an appropriate error to raise, when given response from server has an unexpected content type. """
    if 'Content-Type' in resp.headers:
        return InsightServerResponseError(f"Insight server returned unexpected content type "
                                          f"'{resp.headers['Content-Type']}' from "
                                          f"endpoint '{resp.request.url}'")
    return InsightServerResponseError(f"Insight server returned unexpected content type from "
                                      f"endpoint '{resp.request.url}'")


def make_json_parsing_error(resp: requests.Response) -> InsightServerResponseError:
    """ Return an appropriate error to raise, when given response from server has an unexpected content type. """
    return InsightServerResponseError(f"Insight server returned invalid or unexpected JSON data from "
                                      f"endpoint '{resp.request.url}'")
