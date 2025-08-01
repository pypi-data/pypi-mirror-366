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

from contextlib import AbstractContextManager
from datetime import datetime, timezone, timedelta
import sys
import threading
from typing import Optional, Callable, Union, Iterable, Type, Dict, List, Tuple
import urllib.parse

import keyring
import requests
from pydantic import BaseModel, ValidationError, RootModel
from requests.adapters import HTTPAdapter, Retry
from requests_toolbelt import MultipartEncoder

from ..slow_tasks_monitor import SlowTasksMonitor
from .apps import InsightAppOperations
from .auth import BearerToken, BearerTokenAuth, NoAuth
from .folders import InsightFolderOperations
from .errors import make_insight_server_error, make_unexpected_content_type_error, make_json_parsing_error
from .executions import InsightExecutionOperations
from .models import BearerTokenRequest, DmpIamBearerTokenRequest, DmpIamBearerTokenResponse, Page
from .rest_client_base import (R, INSIGHT_JSON_CONTENT_TYPE, INSIGHT_TEXT_CONTENT_TYPE,
                               is_json_content_type, is_text_content_type)
from .scenarios_data import InsightScenarioDataOperations
from .scenarios import InsightScenarioOperations
from .users import InsightUserOperations

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override


class InsightRestClientConfig(threading.local):
    """
    Defines object onto which a caller can write additional config to be applied to any InsightRestClient instance
    created on this thread. Values are read by the constructor so changing configuration here will not affect any
    InsightRestClient instances that already exist.

    Attributes
    ----------
    slow_tasks_monitor: Optional[SlowTasksMonitor]
        Object used to monitor and warn of any slow-running tasks within the REST client.
    """
    slow_tasks_monitor: Optional[SlowTasksMonitor] = None


#
#
#
rest_client_config = InsightRestClientConfig()


# pylint: disable-next=too-many-ancestors,too-few-public-methods
class InsightRestClient(InsightAppOperations,
                        InsightExecutionOperations,
                        InsightFolderOperations,
                        InsightScenarioOperations,
                        InsightScenarioDataOperations,
                        InsightUserOperations,
                        AbstractContextManager):
    """
    Allows interaction with an Insight v5 server through its REST API.  Supports a commonly-used subset of the Insight
    5 REST API operations, allowing a Python script to create, update, and delete apps, folders and scenarios; to read
    and write entity data; to access and update scenario and app attachments, as well as to execute scenarios.

    `InsightRestClient` can be used both inside and outside Insight apps. When used within an Insight
    scenario, there is no relationship between the calls made through `xpressinsight.scenario` and the currently
    running scenario (any reads or writes behave as though they came from outside the scenario).

    Examples
    --------

    Example of initializing an `InsightRestClient` and using it to make a request.  (Client ID and Secret must have
    been saved in the keychain.)

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     user = client.get_user('570b9100-46e3-4643-baee-2e24aa538f25')
    ...     print(f'Found user {user.name} <{user.email}>')


    Example of initializing an `InsightRestClient` within an Insight app running within DMP and using it to make a
    request back to the same Insight server:

    >>> with self.insight.get_rest_client() as client:
    ...     user = client.get_user('570b9100-46e3-4643-baee-2e24aa538f25')
    ...     print(f'Found user {user.name} <{user.email}>')

    Notes
    -----

    `InsightRestClient` can be used as a context manager to ensure rapid cleanup of any resources (HTTP sessions, etc.).

    See Also
    --------

    AppInterface.get_rest_client
    """
    def __init__(self,
                 insight_url: str,  #
                 client_id: Optional[str] = None,
                 secret: Optional[str] = None,
                 dmp_iam_url: Optional[str] = None,
                 bearer_token_provider: Optional[Callable[[], BearerToken]] = None,
                 max_retries: int = 5,
                 verify_credentials: bool = True,
                 slow_task_threshold: timedelta = timedelta(minutes=2),
                 ):
        """
        Creates a new `InsightRestApi` instance, which can be used to interact with an Insight v5 server through its
        REST API.  Requests made will be authorized using the user for which the `client_id` and `secret` were
        generated.

        The `InsightRestApi` should be constructed in this way when being used from outside an Insight app; when
        connecting to the same server currently executing this Python code,
        use :fct-ref:`AppInterface.get_rest_client` instead.

        Parameters
        ----------
        insight_url : str
            The URL of the Insight server to access. If copying a URL from the browser, the trailing "/insight"
            should not be included. For example, `"http://localhost:8080/"`
        client_id : str, optional
            The client ID value to use to authenticate the session with the Insight server.  If not specified, the
            client ID is read from the system keyring entry `"ficoxpress:<insight_url>"`.
        secret : str, optional
            The secret value to use to authenticate the session with the Insight server.  If not specified,
            the secret is read from the system keyring entry `"ficoxpress:<insight_url>"`.  If client_id was
            specified, keyring will specifically look for an entry with that name and client_id.
        dmp_iam_url : str, optional
            The URL of the DMP IAM endpoint to use to authenticate a session with an Insight component in DMP.
            This is `"https://iam-svc.<domain_name>/registration/rest/client/security/token"` where `<domain_name>`
            is the domain for the DMP instance you're using; for example
            `"https://iam-svc.mydms.usw2.ficoanalyticcloud.com/registration/rest/client/security/token"`.
        bearer_token_provider : Callable[[],BearerToken], optional
            Function that will return a `BearerToken` to use to authorize requests to the Insight server. In
            advanced use cases, a function pointer can be provided as an alternative to specifying the
            `client_id` and `secret` and allowing `InsightRestClient` to authorize itself.
        max_retries : int, optional
            The maximum number of times to attempt to retry a failed request before giving up.  Defaults to 5.
        verify_credentials : bool, optional
            Whether to immediately fetch a bearer token and verify that the `client_id` and `secret` values are
            correct. Defaults to `True`. If set to `False`, this function will not raise an error if the credentials
            are invalid; instead, an error is raised from the function that calls out to the Insight REST API.
        slow_task_threshold : timedelta, default 2 minutes
            Requests and internal tasks taking this time or longer will result in warnings output to the run log.
            This is a troubleshooting setting that can be used to track if internal xpressinsight operations
            are being unexpectedly time-consuming.

        Raises
        ------
        ValueError:
            If sufficient credentials to authenticate are not passed to this function.
        scenario.AuthenticationError
            If authentication with the supplied credentials is unsuccessful.
        scenario.InsightServerError
            If there is an issue communicating with the Insight or IAM server.

        Examples
        --------
        Example of obtaining an `InsightRestClient` to communicate with an on-premise Insight server, with the
        clientID and secret stored in the keyring entry `'ficoxpress:http://localhost:8080/'` (recommended pattern
        on Windows):

        >>> client = InsightRestClient(insight_url='http://localhost:8080')

        Example of obtaining an `InsightRestClient` to communicate with an on-premise Insight server, reading the
        secret stored in the keyring entry `'ficoxpress:http://localhost:8080/'` for the given client ID (recommended
        on Mac):

        >>> MY_CLIENT_ID: str = '<copy client id from Insight UI to here>'
        ... client = InsightRestClient(insight_url='http://localhost:8080',
        ...                            client_id=MY_CLIENT_ID)

        Example of obtaining an `InsightRestClient` to communicate with an on-premise Insight server, passing the
        credentials as plain text:

        >>> MY_CLIENT_ID: str = '<copy client id from Insight UI to here>'
        ... MY_SECRET: str = '<copy secret from Insight UI to here>'
        ... client = InsightRestClient(
        ...     insight_url='http://localhost:8080',
        ...     client_id=MY_CLIENT_ID, secret=MY_SECRET)

        Example of obtaining an `InsightRestClient` to communicate with an Insight component on DMP:

        >>> MY_CLIENT_ID: str = '<copy client id from DMP UI to here>'
        ... MY_SECRET: str = '<copy secret from DMP UI to here>'
        ... IAM_SERVER = 'https://iam-svc.dms.usw2.ficoanalyticcloud.com'
        ... IAM_URL = f'{IAM_SERVER}/registration/rest/client/security/token'
        ... client = InsightRestClient(
        ...     insight_url='https://app.dms.usw2.ficoanalyticcloud.com/16m0jgaeei',
        ...     dmp_iam_url=IAM_URL,
        ...     client_id=MY_CLIENT_ID, secret=MY_SECRET)

        Notes
        -----

        When using `InsightRestClient` from within an Insight scenario to communicate with the same Insight v5
        server, it's recommended to use the :fct-ref:`AppInterface.get_rest_client` rather than calling this
        constructor directly.

        If client_id or secret are not specified, the Python "keyring" package will be used to read the credentials
        from a keyring named `"ficoxpress:<insight_url>"` (where `<insight_url>` is the URL as passed to this
        function).  When this class is used outside an Insight app (e.g. from a standalone Python script), it's
        recommended apps follow this pattern to ensure the credentials are passed in securely.

        On Windows, client_id and secret should be stored in the "generic credentials" area of the Windows credential
        manager; the secret should not be passed to this function. The client_id can also be omitted, but can be
        included if required (in which case the stored credentials will only be used if the stored client_id matches
        the one passed in).

        On Mac, the "keyring" package cannot read the client_id value from the keychain. You should create an
        "application password" entry in the keychain with the client_id and secret, but the client_id value should
        also be passed to this function.

        If using the `client_id` and `secret` from the "Client Apps" page in the DMP user interface, the
        requests to the Insight server are made as a user named `solutionclient`.  By default, this user can
        access very little. You might need to add this user to apps, or give it additional authorities, using the
        Insight administration UI.

        `InsightRestClient` can be used as a context manager to ensure rapid cleanup of any resources (HTTP sessions,
        etc.).

        See Also
        --------

        AppInterface.get_rest_client
        """

        #
        if not insight_url:
            raise ValueError("insight_url must be specified")
        if secret and not client_id:
            raise ValueError("client_id must be provided if secret is given.")
        if bearer_token_provider and (client_id or secret):
            raise ValueError("Only one of bearer_token_provider and client_id/secret pair may be provided")
        if dmp_iam_url is not None and not dmp_iam_url:
            raise ValueError("auth_url must be a valid URL")
        if not isinstance(max_retries, int) or max_retries < 0:
            raise ValueError("max_retries must be a positive integer")

        #
        self.__insight_url = insight_url
        self.__dmp_iam_url = dmp_iam_url
        self.__slow_tasks_monitor = rest_client_config.slow_tasks_monitor or SlowTasksMonitor(slow_task_threshold)
        if not bearer_token_provider:
            if secret:
                self.__client_id = client_id
                self.__secret = secret
            else:
                try:
                    (self.__client_id, self.__secret) = InsightRestClient._get_credentials_from_keyring(insight_url,
                                                                                                        client_id)
                except KeyError as e:
                    raise ValueError(f'Could not find credentials for Insight server URL "{self.__insight_url}". '
                                     f'Either pass client_id/secret arguments when creating InsightRestClient or '
                                     f'create entry "ficoxpress:{self.__insight_url}" in system keyring.') from e

            if dmp_iam_url:
                bearer_token_provider = self._get_bearer_token_from_dmp_iam
            else:
                bearer_token_provider = self._get_bearer_token_from_insight_server
        self.__bearer_token_auth = BearerTokenAuth(bearer_token_provider)

        #
        self.__session = requests.Session()
        self.__session.auth = self.__bearer_token_auth
        if max_retries > 0:
            retries = Retry(total=max_retries, backoff_factor=.1,
                            #
                            status_forcelist=[500, 502, 503, 504],
                            #
                            #
                            #
                            allowed_methods=None,
                            raise_on_status=False)
            self.__session.mount(self.__insight_url, HTTPAdapter(max_retries=retries))
            if self.__dmp_iam_url:
                self.__session.mount(self.__dmp_iam_url, HTTPAdapter(max_retries=retries))

        #
        if verify_credentials:
            self.__session.auth.refresh_bearer_token()

    def __exit__(self, exc_type, exc_value, traceback):
        self.__session.close()

    @property
    def _session(self) -> requests.Session:
        return self.__session

    @property
    def _slow_tasks_monitor(self) -> SlowTasksMonitor:
        return self.__slow_tasks_monitor

    @staticmethod
    def _get_credentials_from_keyring(insight_url: str, client_id: Optional[str]) -> Optional[Tuple[str, str]]:
        """ Try to fetch credentials from keyring; return a (client_id, secret) tuple if found.
            Raise KeyError if not found. """
        for name in InsightRestClient._get_possible_keyring_entry_names(insight_url):
            credentials = keyring.get_credential(name, username=client_id)
            if credentials:
                return credentials.username, credentials.password

        raise KeyError(f'Credentials for "{insight_url}" not found in keyring.')

    @staticmethod
    def _get_possible_keyring_entry_names(insight_url: str) -> List[str]:
        #
        names = [f'ficoxpress:{insight_url}']
        #
        if insight_url.endswith('/'):
            names.append(f'ficoxpress:{insight_url[:-1]}')
        else:
            names.append(f'ficoxpress:{insight_url}/')
        return names

    def _get_bearer_token_from_insight_server(self) -> BearerToken:
        #
        token_max_age = 15*60  #
        #
        #
        token_expiry = datetime.now(tz=timezone.utc) + timedelta(seconds=token_max_age)
        token = self._make_json_request('POST', '/api/authentication/token', auth=False,
                                        response_type=str,
                                        request_body=BearerTokenRequest(client_id=self.__client_id,
                                                                        secret=self.__secret,
                                                                        max_age=token_max_age))
        return BearerToken(token=token, expires=token_expiry)

    def _get_bearer_token_from_dmp_iam(self) -> BearerToken:
        #
        # pylint: disable-next=line-too-long
        #
        request_body = DmpIamBearerTokenRequest(client_id=self.__client_id, secret=self.__secret)
        response = self.__session.request('POST', url=self.__dmp_iam_url, auth=NoAuth(),
                                          headers={'Content-Type': 'application/json',
                                                   'Accept': 'application/json'},
                                          json=request_body.model_dump(by_alias=True))

        if response.status_code != 200:
            raise make_insight_server_error(response)
        if 'Content-Type' not in response.headers or not is_json_content_type(response.headers['Content-Type']):
            raise make_unexpected_content_type_error(response)

        try:
            json_response = DmpIamBearerTokenResponse.model_validate_json(response.text)
        except ValidationError as e:
            raise make_json_parsing_error(response) from e

        return BearerToken(
            token=json_response.access_token,
            expires=datetime.fromtimestamp(json_response.expiry_timestamp/1000, tz=timezone.utc)
        )

    @override
    def _get_request_url(self, path: Union[str, Iterable[str]]) -> str:
        #
        if isinstance(path, Iterable) and not isinstance(path, str):
            path_components = list(path)
            if not all(isinstance(x, str) for x in path_components):
                raise ValueError("All path components must be strings.")
            if not all(len(x) for x in path_components):
                raise ValueError("A path component must not be an empty string")
            path = path_components[0]
            if not path.endswith('/') and len(path_components) > 1:
                path = path + '/'
            path = path + '/'.join([urllib.parse.quote(c, safe='') for c in path_components[1:]])

        #
        url = self.__insight_url
        if url.endswith('/') and path.startswith('/'):
            url = url[:-1]
        elif not url.endswith('/') and not path.startswith('/') and len(path) > 0:
            url += '/'
        url = url + path
        return url

    @override
    # pylint: disable-next=too-many-arguments
    def _make_json_request(self,
                           method: str,
                           path: Union[str, Iterable[str]],
                           response_type: Type[R],
                           query_params: Optional[Dict] = None,
                           request_body: Optional[Union[BaseModel, Dict, MultipartEncoder]] = None,
                           expected_status_code: int = 200,
                           auth: bool = True
                           ) -> R:
        headers = {}
        request_body_json: Optional[Dict] = None
        request_body_data: Optional[MultipartEncoder] = None

        #
        if request_body is not None:
            if isinstance(request_body, BaseModel):
                request_body_json = request_body.model_dump(by_alias=True)
                headers['Content-Type'] = INSIGHT_JSON_CONTENT_TYPE
            elif isinstance(request_body, Dict):
                request_body_json = request_body
                headers['Content-Type'] = INSIGHT_JSON_CONTENT_TYPE
            elif isinstance(request_body, MultipartEncoder):
                request_body_data = request_body
                headers['Content-Type'] = request_body.content_type
            else:
                raise ValueError(f"Unrecognized request_body type {type(request_body)}")

        #
        accept_types = []
        if response_type is str:
            #
            accept_types.append(INSIGHT_TEXT_CONTENT_TYPE)
        #
        accept_types.append(INSIGHT_JSON_CONTENT_TYPE)
        headers['Accept'] = ','.join(accept_types)

        #
        request_url = self._get_request_url(path)
        with self._slow_tasks_monitor.task(f'InsightRestClient HTTP {method} {request_url}'):
            response = self.__session.request(
                method=method,
                url=request_url,
                params=query_params,
                auth=self.__bearer_token_auth if auth else NoAuth(),
                headers=headers,
                json=request_body_json,
                data=request_body_data
            )

        #
        if response.status_code != expected_status_code:
            raise make_insight_server_error(response)

        content_type = response.headers['Content-Type'] if 'Content-Type' in response.headers else None

        #
        if response_type is None:
            #
            return None

        if response_type is str:
            #
            if not is_text_content_type(content_type):
                raise make_unexpected_content_type_error(response)
            return response.text

        if response_type is Dict:
            #
            if not is_json_content_type(content_type):
                raise make_unexpected_content_type_error(response)
            try:
                response_dict = response.json()
            except requests.JSONDecodeError as e:
                raise make_json_parsing_error(response) from e

            if not isinstance(response_dict, dict):
                raise make_json_parsing_error(response)

            return response_dict

        if issubclass(response_type, BaseModel):
            #
            if not is_json_content_type(content_type):
                raise make_unexpected_content_type_error(response)
            try:
                return response_type.model_validate_json(response.text)
            except ValidationError as e:
                raise make_json_parsing_error(response) from e

        #
        raise ValueError(f"Unrecognized response type '{response_type}'")

    @override
    # pylint: disable-next=too-many-arguments
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
        items = []
        page = None
        next_page = 0
        while page is None or not page.root.last:
            request_query_params = dict(query_params or {})
            request_query_params['page'] = next_page
            request_query_params['size'] = page_size
            page = self._make_json_request(
                method=method,
                path=path,
                response_type=RootModel[Page[item_type]],
                query_params=request_query_params,
                request_body=request_body,
                expected_status_code=expected_status_code,
                auth=auth
            )
            items += page.root.content
            next_page += 1

        return items
