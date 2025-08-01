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

from datetime import datetime, timedelta, timezone
import threading
from typing import Callable, Optional

from pydantic import field_validator, BaseModel, ConfigDict
import requests.auth


class BearerToken(BaseModel):
    """
    Class containing a bearer token that can be used to authorize a request to the Insight 5 REST API, and the
    date/time after which the token is no longer valid.

    Attributes
    ----------
    token : str
        The bearer token string.
    expires : datetime
        The date and time at which the token will expire; must be in the UTC timezone.
    """
    model_config = ConfigDict(validate_assignment=True)
    token: str
    expires: datetime

    @field_validator('expires', mode='before')
    @classmethod
    def _expires_must_be_utc(cls, expires: datetime) -> datetime:
        if expires.tzinfo != timezone.utc:
            raise ValueError("Bearer token expiry timestamp must be in UTC timezone.")
        return expires

    @property
    def is_expiring(self) -> bool:
        """ Check whether the token has expired or will expire within the next 30 seconds. """
        return self.expires - datetime.now(tz=timezone.utc) < timedelta(seconds=30)


class BearerTokenAuth(requests.auth.AuthBase):
    """
    Simple AuthBase implementation for requests that caches a bearer token, fetches it from the given provider
    function if it's expired, and appends it to Authorization headers
    """

    def __init__(self, bearer_token_provider: Callable[[], BearerToken]):
        self.__bearer_token_provider = bearer_token_provider
        self.__current_token: Optional[BearerToken] = None
        self.__token_update_lock = threading.RLock()

    def __call__(self, req):
        #
        with self.__token_update_lock:
            if (self.__current_token is None or self.__current_token.is_expiring):
                self.refresh_bearer_token()

            #
            req.headers['Authorization'] = f"Bearer {self.__current_token.token}"
        return req

    @property
    def current_bearer_token(self) -> Optional[BearerToken]:
        """ Token currently cached within the AuthBase. """
        return self.__current_token

    def refresh_bearer_token(self):
        """ Force a refresh of the bearer token, regardless of time """
        with self.__token_update_lock:
            token = self.__bearer_token_provider()
            self.__current_token = token


class NoAuth(requests.auth.AuthBase):
    """
    Simple AuthBase implementation that does nothing,
    """

    def __call__(self, req):
        return req
