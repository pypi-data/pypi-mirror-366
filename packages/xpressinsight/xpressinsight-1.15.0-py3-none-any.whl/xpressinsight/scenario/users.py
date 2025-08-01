"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly. This defines functions and classes for accessing Insight
    user information through the REST interface.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from abc import ABC
from dataclasses import dataclass, field
import sys

from .common import parse_insight_enum_value
from .rest_client_base import InsightRestClientBase
from . import models
from ..type_checking import XiEnum

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self


class UserStatus(XiEnum):
    """
    Enumeration of the different possible states of a user's account.

    Attributes
    ----------
    ACTIVE : str
        User account is active.
    DELETED : str
        User account is deleted.
    DISABLED : str
        User account is disabled.
    LOCKED : str
        User account is locked.
    """
    ACTIVE = 'ACTIVE'
    DELETED = 'DELETED'
    DISABLED = 'DISABLED'
    LOCKED = 'LOCKED'


@dataclass
class User:
    """
    Information about a user account.

    Attributes
    ----------
    id : str
        The unique ID of this user
    username : str
        This user's username
    name : str
        This user's full name
    first_name : str
        This user's first name
    last_name : str
        This user's last name
    email : str
        This user's email address
    status : UserStatus
        The status of this user's account
    """
    id: str = field(default='')
    username: str = field(default='')
    name: str = field(default='')
    first_name: str = field(default='')
    last_name: str = field(default='')
    email: str = field(default='')
    status: UserStatus = field(default=UserStatus.ACTIVE)

    @classmethod
    def _from_rest_api_model(cls, src: models.User) -> Self:
        return User(
            id=src.id,
            username=src.username,
            name=src.name,
            first_name=src.first_name,
            last_name=src.last_name,
            email=src.email,
            status=parse_insight_enum_value(UserStatus, src.status)
        )


class InsightUserOperations(InsightRestClientBase, ABC):
    """
    Implementation of calls to user- and privilege-related endpoints in the Insight REST API.
    """

    def get_user(self, user_id: str) -> User:
        """
        Get the user record with the specified ID.

        Parameters
        ----------
        user_id : str
            The ID of the user to query.

        Returns
        -------
        user : User
            Information about the user with the requested ID.

        Raises
        ------
        scenario.ItemNotFoundError
            If there is no user account with this ID, or the REST API client credentials do not have permission to
            access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     user = client.get_user('570b9100-46e3-4643-baee-2e24aa538f25')
        ...     print(f'Found user {user.name} <{user.email}>')

        Notes
        -----

        Accessing information for other users will require the `SYS_USER` authority.
        """
        user = self._make_json_request(
            method='GET',
            path=['api', 'admin', 'users', user_id],
            response_type=models.User
        )

        # noinspection PyProtectedMember
        # pylint: disable-next=protected-access
        return User._from_rest_api_model(user)
