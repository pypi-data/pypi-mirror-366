"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly.

    Defines various common structures used by the Insight Python REST API
    client.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
# pylint: disable=protected-access,too-many-instance-attributes,too-many-arguments,too-few-public-methods

from dataclasses import dataclass
from datetime import datetime
import sys
from typing import Optional, TypeVar, Type

from dateutil.parser import parse as parse_datetime

from .errors import InsightServerResponseError
from . import models
from ..type_checking import XiEnum

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self


class ObjectType(XiEnum):
    """
    Enumeration of the different types of object that can be returned by the Insight server.

    Attributes
    ----------

    APP : str
        App object
    FOLDER : str
        Folder object
    SCENARIO : str
        Scenario object
    USER : str
        User object
    """
    APP = "APP"
    ATTACHMENT = "ATTACHMENT"
    FOLDER = "FOLDER"
    SCENARIO = "SCENARIO"
    USER = "USER"


def get_rest_resource_name(t: ObjectType) -> str:
    """ Get the resource name used in endpoints to access objects of this type (where relevant) """
    if t == ObjectType.APP:
        return "apps"

    if t == ObjectType.FOLDER:
        return "folders"

    if t == ObjectType.SCENARIO:
        return "scenarios"

    raise ValueError(f"No endpoint name configured for object type {t}")


@dataclass
class Reference:
    """
    Class containing an ID and object type; used to refer to other objects in the Insight
    data model where the type cannot be inferred from the context.

    Attributes
    ----------

    id : str
        The unique ID of the item.
    type : ObjectType
        The type of the item.
    name : str, optional
        The name of the item. This is included for information purposes when a Reference is fetched
        from the Insight server; it does not need to be populated when a Reference is passed to
        the Insight server.
    """
    id: str
    type: ObjectType
    name: Optional[str] = None

    @classmethod
    def to_app(cls, app_id) -> Self:
        """
        Shorthand for creating a Reference to an app of the given ID. Equivalent to
        `ins.Reference(id=app_id, type=ins.ObjectType.APP)`.

        Examples
        --------
        >>> app_reference = ins.Reference.to_app(self.insight.app_id)
        """
        return Reference(id=app_id, type=ObjectType.APP)

    @classmethod
    def to_folder(cls, folder_id) -> Self:
        """
        Shorthand for creating a Reference to a folder of the given ID. Equivalent to
        `ins.Reference(id=app_id, type=ins.ObjectType.FOLDER)`.

        Examples
        --------
        >>> FOLDER_ID = '570b9100-46e3-4643-baee-2e24aa538f25'
        ... folder_reference = ins.Reference.to_folder(FOLDER_ID)
        """
        return Reference(id=folder_id, type=ObjectType.FOLDER)

    @classmethod
    def to_scenario(cls, folder_id) -> Self:
        """
        Shorthand for creating a Reference to a folder of the given ID. Equivalent to
        `ins.Reference(id=app_id, type=ins.ObjectType.SCENARIO)`.

        Examples
        --------
        >>> SCENARIO_ID = '570b9100-46e3-4643-baee-2e24aa538f25'
        ... folder_reference = ins.Reference.to_scenario(SCENARIO_ID)
        """
        return Reference(id=folder_id, type=ObjectType.SCENARIO)

    @classmethod
    def _from_rest_api_model(cls, src: Optional[models.Reference]) -> Optional[Self]:
        """ Convert a Reference object as returned by the Insight REST API to one that we want to present to
            the app developer. """
        if src is None:
            return None

        return Reference(
            id=src.id,
            type=parse_insight_enum_value(ObjectType, src.object_type),
            name=src.name
        )

    def _to_rest_api_model(self) -> models.Reference:
        """ Convert a Reference object as supplied by the app developer into a Reference object we can pass to
            the Insight REST API. """
        return models.Reference(id=self.id, object_type=self.type.name, name=self.name)


class ShareStatus(XiEnum):
    """
    Enumeration of the different ways a scenario or folder can be shared with other users.

    Attributes
    ----------

    FULLACCESS : str
        The scenario has been shared with all users
    PRIVATE : str
        The scenario has not been shared with any other users
    READONLY : str
        The scenario can be read by other users, but not modified
    """
    FULLACCESS = 'FULLACCESS'
    PRIVATE = 'PRIVATE'
    READONLY = 'READONLY'


E = TypeVar('E', bound=XiEnum)


def parse_insight_enum_value(enum_type: Type[E], value: Optional[str]) -> Optional[E]:
    """ Parse a string returned by Insight into a value of the given enumeration type.
        Equivalent to calling enum_type[value], except raises InsightServerResponseError if value is
        unrecognized, and returns 'None' if value is None.
    """
    if value is None:
        return None
    try:
        return enum_type[value]
    except KeyError as exc:
        raise InsightServerResponseError(f'Insight server returned unrecognized value "{value}" '
                                         f'for {enum_type.__name__}; allowed values '
                                         'are: ' + ', '.join([f'"{e.name}"' for e in list(enum_type)])) from exc


def parse_insight_datetime(value: Optional[str]) -> Optional[datetime]:
    """ Insight REST API returns datetimes as number of seconds since 1/1/1970 - convert this to Python datetime. """
    if value is None:
        return None

    try:
        return parse_datetime(value)
    except ValueError as exc:
        raise InsightServerResponseError(f'Insight server returned unrecognized value "{value}" for '
                                         f'datetime field') from exc
