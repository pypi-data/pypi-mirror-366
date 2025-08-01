"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Utilities relating to checking and transforming types of values in various ways.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
import re
import sys
from enum import Enum
from typing import Any, Type, get_origin, get_type_hints, Union, get_args, List, Tuple, TypeVar, Optional

from .entities import BASIC_TYPE, boolean, integer, string, real


def is_value_of_type(val: Any, expected_type: Type) -> bool:
    """ Check whether the given value is of the expected type.
        Supports expected_type being a Union or an Optional or a BASIC_TYPE as well as other types that
        can be evaluated using isinstance."""

    if get_origin(expected_type) is Union:
        for possible_type in get_args(expected_type):
            if is_value_of_type(val, possible_type):
                return True

        return False

    if expected_type == BASIC_TYPE:
        return isinstance(val, type) and issubclass(val, (boolean, integer, string, real))

    return isinstance(val, expected_type)


def check_simple_python_type(attr: Any, attr_name: str, attr_type: Type, parent: Type = None):
    """ Check value 'attr' is of 'attr_type'. """
    if not is_value_of_type(attr, attr_type):
        attr_name = re.sub(r'_.*__', '', attr_name)
        parent = f"of {parent.__name__} " if parent is not None else ""
        raise TypeError(f'The "{attr_name}" parameter {parent}must be a "{attr_type.__name__}" object, '
                        f'but it is a "{type(attr).__name__}" and has value "{attr}".')


def check_instance_attribute_types(class_instance: Any):
    """ Type check for all instance attributes with class level type hints. """
    class_type = type(class_instance)
    none_type = type(None)

    for attr_name, attr_type in get_type_hints(class_type).items():
        attr = getattr(class_instance, attr_name)

        #
        #
        if get_origin(attr_type) is Union:
            non_none_types = [arg for arg in get_args(attr_type) if arg is not none_type]

            if len(non_none_types) == 1:
                if attr is None:
                    continue

                attr_type = non_none_types[0]

        if attr_type == BASIC_TYPE:
            if not issubclass(attr, (boolean, integer, string, real)):
                attr_name = re.sub(r'_.*__', '', attr_name)
                raise TypeError(f'The "{attr_name}" parameter of "{class_type.__name__}" must be an Insight type '
                                f'string, integer, boolean, or real, but it is a "{type(attr).__name__}" and has '
                                f'value "{attr}".')
        else:
            check_simple_python_type(attr, attr_name, attr_type, class_type)


def python_int_to_bool(value: int, name: str) -> bool:
    """ Convert integer to boolean. The given 'name' will be used in the error message if the value
        is not 0 or 1. """
    if value == int(True):
        return True
    if value == int(False):
        return False
    raise ValueError(
        f'Invalid boolean found in "{name}", expecting {int(True)} (True) or {int(False)} (False) but got "{value}".'
    )


def __get_parent_name(parent_obj_or_none: Any) -> str:
    return '' if parent_obj_or_none is None else ' of ' + type(parent_obj_or_none).__name__


T = TypeVar("T")

def validate_list(parent_obj_or_none: Any, attr_name: str, item_type: Type[T], item_type_name: str,
                  value: Union[List[T], Tuple[T, ...], T]) -> Tuple[T, ...]:
    """
    Given a list/tuple, verify all the values are of the expected type and convert to an immutable tuple.
    If the given value is a single item, return that item.validate_list

    Parameters
    ----------
    parent_obj_or_none : Any
        Parent object, used in error messages only.
    attr_name : str
        Name of attribute being validated, used in error messages only.
    item_type : Type[T]
        Type of items expected in list.
    item_type_name : str
        Name of expected item type
    value :
        Collection of items to evaluate
    """

    if is_value_of_type(value, item_type):
        return (value,)

    error_msg = 'The "{0}" parameter{1} must be a {2} object or a list of {2} objects, '

    if isinstance(value, list):
        value = tuple(value)

    if isinstance(value, tuple):
        if len(value) == 0:
            raise TypeError((error_msg + 'but the {0} list is empty.')
                            .format(attr_name, __get_parent_name(parent_obj_or_none), item_type_name))

        for item in value:
            if not is_value_of_type(item, item_type):
                raise TypeError((error_msg + 'but the {0} list contains an object of type "{3}" and value: {4}.')
                                .format(attr_name, __get_parent_name(parent_obj_or_none), item_type_name,
                                        type(item).__name__, repr(item)))
    else:
        raise TypeError((error_msg + 'but the {0} parameter has type "{3}" and value: {4}.')
                        .format(attr_name, __get_parent_name(parent_obj_or_none), item_type_name,
                                type(value).__name__, repr(value)))
    return value


def validate_optional_list(parent_obj_or_none: Any, attr_name: str, item_type: Type[T], item_type_name: str,
                           value: Optional[Union[List[T], Tuple[T, ...], T]]) -> Optional[Tuple[T, ...]]:
    """
    Given a list/tuple, verify all the values are of the expected type and convert to an immutable tuple.
    If the given value is a single item, return that item.validate_list.  If given no value or an empty list,
    return None.

    Parameters
    ----------
    parent_obj_or_none : Any
        Parent object, used in error messages only.
    attr_name : str
        Name of attribute being validated, used in error messages only.
    item_type : Type[T]
        Type of items expected in list.
    item_type_name : str
        Name of expected item type
    value :
        Collection of items to evaluate
    """
    if not value:
        return None

    return validate_list(parent_obj_or_none, attr_name, item_type, item_type_name, value)


class XiEnum(Enum):
    """
    The base class for `Enum` types in the `xpressinsight` package.
    """

    def __repr__(self):
        #
        # pylint: disable-next=no-member
        return f"{self.__class__.__name__}.{self._name_}"
