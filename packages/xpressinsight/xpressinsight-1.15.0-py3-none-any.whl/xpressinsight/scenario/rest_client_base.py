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
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, TypeVar, Type, Union, Iterable, List

import requests
from pydantic import BaseModel
from requests_toolbelt import MultipartEncoder

from ..slow_tasks_monitor import SlowTasksMonitor


INSIGHT_JSON_CONTENT_TYPE = "application/vnd.com.fico.xpress.insight.v2+json"
INSIGHT_BINARY_CONTENT_TYPE = "application/vnd.com.fico.xpress.insight.v2+octet-stream"
INSIGHT_TEXT_CONTENT_TYPE = "text/vnd.com.fico.xpress.insight.v2+plain"


def is_json_content_type(content_type: Optional[str]) -> bool:
    """ Check if the given content-type string represents JSON content. """
    return (content_type is not None and
            re.match(r"application/(.*\+)?json( *;.*)?", content_type) is not None)


def is_text_content_type(content_type: Optional[str]) -> bool:
    """ Check if the given content-type string represents plain text content. """
    return (content_type is not None and
            re.match(r"text/(.*\+)?plain( *;.*)?", content_type) is not None)


def is_binary_content_type(content_type: Optional[str]) -> bool:
    """ Check if the given content-type string represents binary content. """
    return (content_type is not None and
            re.match(r"application/(.*\+)?octet-stream( *;.*)?", content_type) is not None)


#
R = TypeVar('R')


class InsightRestClientBase(ABC):
    """
    Abstract base class for classes implementing operations that call the REST API.

    Allows for the different operations to be split between different class files, for code organisation purposes.
    """

    @property
    @abstractmethod
    def _session(self) -> requests.Session:
        """ Read the Session object to be used for communicating with the Insight server. """

    @property
    @abstractmethod
    def _slow_tasks_monitor(self) -> SlowTasksMonitor:
        """ Read the object that's used to warn of slow operations. """

    @abstractmethod
    def _get_request_url(self, path: Union[str, Iterable[str]]) -> str:
        """
        Construct a URL for making a request to the Insight server.

        Parameters
        ----------
        path: str or Iterable[str]
            The path of the endpoint to call, e.g. `/api/admin/users`. Can be passed as either a string or
            a list of path components; in the case of a list, the first item is expected to be the 'root path'
            and used verbatim, then subsequent items are URLencoded and appended to this with '/' as a separator.
        """

    @abstractmethod
    def _make_json_request(self,
                           method: str,
                           path: Union[str, Iterable[str]],
                           response_type: Type[R],
                           query_params: Optional[Dict] = None,
                           request_body: Optional[Union[BaseModel, Dict, MultipartEncoder]] = None,
                           expected_status_code: int = 200,
                           auth: bool = True
                           ) -> R:
        """
        Make an HTTP request to the given path on the Insight server, expecting a JSON document in response.
        Detect errors and generate appropriate exception.

        Parameters
        ----------
        method: str
            The HTTP method to use, one of: GET, OPTIONS, HEAD, POST, PUT, PATCH, DELETE.
        path: str or Iterable[str]
            The path of the endpoint to call, e.g. `/api/admin/users`. Can be passed as either a string or
            a list of path components; in the case of a list, the first item is expected to be the 'root path'
            and used verbatim, then subsequent items are URLencoded and appended to this with '/' as a separator.
        response_type: Type[BaseModel] or Type[str]
            Type of the expected response to parse; may be a Pydantic model type to parse as JSON, or 'str' to parse
            to a string.
        query_params: Dict, optional
            Additional query parameters to include in request.
        request_body: BaseModel or Dict or MultipartEncoder, optional
            The request body. Should be either a Pydantic model object, or a dictionary (for JSON bodies)
            or a MultipartEncoder (for multipart/form-data request bodies),
        expected_status_code: int, optional
            The status code to expect; any response other than this is treated as an error and an exception will
            be raised.
        auth: bool, optional
            Whether we need add the Authorization header to this request

        Returns
        -------
        R
            The body of the HTTP response, parsed into the specified JSON type.

        Raises
        ------
        InsightServerCommunicationError
            If there is an issue sending data to or receiving data from the Insight server
        InsightServerResponseError
            If the Insight server itself raises an error
        AuthenticationError:
            If there is an issue authenticating with the Insight server.
        AuthorizationError:
            If the current user does not have permission to perform the requested operation.
        """

    @abstractmethod
    def _make_paged_json_request(self,
                                 method: str,
                                 path: Union[str, Iterable[str]],
                                 item_type: Type[R],
                                 query_params: Optional[Dict] = None,
                                 request_body: Optional[Union[BaseModel, Dict, MultipartEncoder]] = None,
                                 expected_status_code: int = 200,
                                 auth: bool = True,
                                 page_size: int = 50
                                ) -> List[R]:
        """
        Make an HTTP request to the given path on the Insight server, expecting a JSON document in response, that
        returns a JSON structure in the standard 'Page' Insight format.  This will repeat the query multiple times
        until it reaches the last page, and return a list of all the elements.

        In other ways, behaves same as _make_json_request.
        """
