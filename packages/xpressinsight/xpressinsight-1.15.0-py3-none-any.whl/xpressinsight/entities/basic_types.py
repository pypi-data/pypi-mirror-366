"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Functionality relating to representation and validation of 'basic' (ie single-value) types and their values.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from typing import TypeVar, Generic, Type, Dict, Union, Any, Optional

import numpy as np
import pandas as pd
from packaging import version

from .. import polars_shims as pl


#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
MAX_STR_LENGTH_BYTES = 1000000
MAX_STR_LENGTH_CHARS = int(MAX_STR_LENGTH_BYTES / 4)

BASIC_TYPE_VALUE = TypeVar('BASIC_TYPE_VALUE', bool, int, str, float)


# pylint: disable-next=too-few-public-methods
class BasicType(Generic[BASIC_TYPE_VALUE]):
    """ Abstract superclass for Insight basic types.

    See Also
    --------

    boolean
    integer
    real
    string
    """


# noinspection PyPep8Naming
#
# pylint: disable-next=invalid-name,too-few-public-methods
class boolean(BasicType[bool]):
    """
    Declare the entity to be (or to contain) boolean (`True` or `False`) values.
    If not specified, the default value is `False`.

    Examples
    --------
    Example of declaring a scalar entity to be boolean.

    >>> my_bool: xi.types.Scalar(dtype=xi.boolean)
    ... my_bool: xi.types.Scalar(False)
    ... my_bool: xi.types.Scalar(True)

    See Also
    --------
    Scalar
    Param
    Index
    Series
    Column
    """


# noinspection PyPep8Naming
#
# pylint: disable-next=invalid-name,too-few-public-methods
class integer(BasicType[int]):
    """
    Declare the entity to be (or to contain) integer (whole number) values.
    Each value must fit into a signed 32-bit integer.
    If not specified, the default value is `0`.

    Examples
    --------
    Example of declaring a scalar entity to be integer.

    >>> my_int: xi.types.Scalar(dtype=xi.integer)
    ... my_int: xi.types.Scalar(0)
    ... my_int: xi.types.Scalar(100)
    ... my_int: xi.types.Scalar(-10)

    See Also
    --------
    Scalar
    Param
    Index
    Series
    Column
    """


#
# noinspection PyPep8Naming
#
# pylint: disable-next=invalid-name,too-few-public-methods
class string(BasicType[str]):
    """
    Declare the entity to be (or to contain) string (UTF-8 encoded) values. The length
    (in bytes) of a string scalar (Scalar or Param) must not exceed 1,000,000 bytes.
    The length of a string in a container (Index, Series, or DataFrame) must not exceed
    250,000 characters. A string must not contain the null character.
    If not specified, the default value of a string scalar is the empty string `""`.

    Examples
    --------
    Example of declaring a scalar entity to be a string.

    >>> my_string: xi.types.Scalar(dtype=xi.string)
    ... my_string: xi.types.Scalar("Hello World!")

    See Also
    --------
    Scalar
    Param
    Index
    Series
    Column
    """


# noinspection PyPep8Naming
#
# pylint: disable-next=invalid-name,too-few-public-methods
class real(BasicType[float]):
    """
    Declare the entity to be (or to contain) floating-point (whole number) values.
    If not specified, the default value is `0.0`.

    Examples
    --------
    Example of declaring a scalar entity to be a floating-point value.

    >>> my_real: xi.types.Scalar(dtype=xi.real)
    >>> my_real: xi.types.Scalar(100.0)
    >>> my_real: xi.types.Scalar(123.456)

    See Also
    --------
    Scalar
    Param
    Index
    Series
    Column
    """


ALL_BASIC_TYPE = [boolean, integer, string, real]
BASIC_TYPE = Type[BasicType]

#
#
#
BASIC_TYPE_MAP: Dict[Type[BasicType], Type] = {
    boolean: bool,
    integer: int,
    string: str,
    real: float,
    #
    None: Union[bool, int, str, float]
}

#
#
#
#
PANDAS_DTYPE_TYPES_FOR_INSIGHT_TYPES = Union[pd.BooleanDtype, pd.StringDtype, pd.Int64Dtype, pd.Float64Dtype] \
                                       if version.parse(pd.__version__) >= version.parse('2.0.0') \
                                       else Type

#
BASIC_PANDAS_DTYPE_MAP: Dict[Type[BasicType], PANDAS_DTYPE_TYPES_FOR_INSIGHT_TYPES] = {
    boolean: np.bool_,
    integer: np.int64,
    string: str,
    real: np.float64,
}

#
BASIC_POLARS_DTYPE_MAP: Dict[Type[BasicType], pl.DataType] = {
    boolean: pl.Boolean(),
    integer: pl.Int64(),
    string: pl.Utf8(),
    real: pl.Float64(),
} if pl.polars_available else {}

#
SCALAR_DEFAULT_VALUES: Dict[Type[BasicType], Union[bool, int, str, float]] = {
    boolean: False,
    integer: 0,
    string: "",
    real: 0.0,
}


def get_basic_type_for_python_type(src_type: Type, entity_name: str) -> Type[BasicType]:
    """ Given some value type, get the appropriate basic type value. The supplied entity_name is used in the
        error message raised if the given type cannot be matched against a BasicType."""
    pd_dtype = pd.api.types.pandas_dtype(src_type)

    if pd.api.types.is_bool_dtype(pd_dtype):
        return boolean

    if pd.api.types.is_integer_dtype(pd_dtype):
        return integer

    if pd.api.types.is_float_dtype(pd_dtype):
        return real

    if pd.api.types.is_string_dtype(pd_dtype):
        return string

    raise TypeError(f'Unable to determine XpressInsight data type for source type "{src_type}" '
                    f'found in entity "{entity_name}".')


def check_str(value: Any) -> bool:
    """ Check if a value is a valid exportable string. """
    return isinstance(value, str) and len(value) <= MAX_STR_LENGTH_CHARS and '\0' not in value


def check_type_np(arr: np.ndarray, value_type: Type[BasicType], name: str):
    """ Check if type of NumPy array 'arr' is compatible with type 'value_type' and check bounds."""
    if arr.size == 0:
        return

    if value_type == string:
        #
        #
        if not np.all(np.vectorize(check_str)(arr)):
            raise TypeError(f"""
            All values in {name} must be strings,
            must not be longer than {MAX_STR_LENGTH_CHARS} characters,
            and must not contain the null character "\\0".
            """)

    elif value_type == integer:
        if arr.dtype.kind != "i":
            raise TypeError(f"""
            All values in {name} must be integers, but the data type is: {arr.dtype}.
            """)

        #
        int32_limits = np.iinfo(np.int32)
        values = arr

        if not (
                np.all(int32_limits.min <= values) and np.all(values <= int32_limits.max)
        ):
            raise TypeError(f"""
            All values in {name} must fit into signed 32-bit integers.
            """)

    elif value_type == real:
        if arr.dtype.kind != "f":
            raise TypeError(f"""
            All values in {name} must be floats, but the data type is: {arr.dtype}.
            """)

        if np.finfo(arr.dtype).bits > 64:
            raise TypeError(f"""
            All values in {name} must fit into 64-bit floats.
            """)

    elif value_type == boolean:
        if arr.dtype.kind != "b":
            raise TypeError(f"""
            All values in {name} must be Booleans, but the data type is: {arr.dtype}.
            """)

    else:
        raise ValueError(f'Unexpected type "{value_type}" passed to check_type_np for "{name}"')


def check_type_pl(ser: pl.Series, value_type: Type[BasicType], name: str):
    """ Check if type of Polars series 'ser' is compatible with type 'value_type' and check bounds."""
    #
    if len(ser) == 0:
        return

    if value_type == string:
        if not isinstance(ser.dtype, pl.Utf8):
            raise TypeError(f"""
                All values in {name} must be strings, but the data type is: {ser.dtype}.
                """)

        if (pl.DataFrame({'ser': ser})
                .filter([
                    pl.col('ser').str.len_chars().gt(MAX_STR_LENGTH_CHARS).or_(
                        pl.col('ser').str.contains('\0', literal=True)
                    )
                ]).height > 0
        ):
            raise TypeError(f"""
                All values in {name} must be strings,
                must not be longer than {MAX_STR_LENGTH_CHARS} characters,
                and must not contain the null character "\\0".
                """)

    elif value_type == integer:
        if not ser.dtype.is_integer():
            raise TypeError(f"""
            All values in {name} must be integers, but the data type is: {ser.dtype}.
            """)

        #
        int32_limits = np.iinfo(np.int32)
        smallest = ser.min()
        largest = ser.max()

        if (smallest is not None and largest is not None and
                smallest < int32_limits.min or largest > int32_limits.max):
            raise TypeError(f"""
            All values in {name} must fit into signed 32-bit integers.
            """)

    elif value_type == real:
        if not ser.dtype.is_float():
            raise TypeError(f"""
            All values in {name} must be floats, but the data type is: {ser.dtype}.
            """)

        if not isinstance(ser.dtype, (pl.Float32, pl.Float64)):
            raise TypeError(f"""
            All values in {name} must fit into 64-bit floats.
            """)

    elif value_type == boolean:
        if not isinstance(ser.dtype, pl.Boolean):
            raise TypeError(f"""
            All values in {name} must be Booleans, but the data type is: {ser.dtype}.
            """)

    else:
        raise ValueError(f'Unexpected type "{value_type}" passed to check_type_np for "{name}"')


def check_basic_type_value(dtype: Optional[BASIC_TYPE], value: Any, entity_name: str):
    """ Verify given value can be stored as a given basic type in Insight.
        If dtype is not null, will infer the basic type from the value and then check
        that the value is valid for that type. """
    #
    #
    #

    if dtype is None:
        dtype = get_basic_type_for_python_type(type(value), entity_name=entity_name)

    #
    if (dtype == integer and isinstance(value, bool)) or \
            not isinstance(value, BASIC_TYPE_MAP.get(dtype)):
        raise TypeError(f"Value {value} has type {type(value).__name__} but should have "
                        f"type {BASIC_TYPE_MAP[dtype].__name__}" +
                        (f" for entity {entity_name}" if entity_name else "") + ".")

    if isinstance(value, str):
        if not len(value.encode("utf-8")) <= MAX_STR_LENGTH_BYTES:
            raise ValueError(f"String must not take more space than {MAX_STR_LENGTH_BYTES} bytes" +
                             (f" when used in entity {entity_name}" if entity_name else "") + ".")

        if '\0' in value:
            raise ValueError(r"String must not contain the null character '\\0'" +
                             (f" when used in entity {entity_name}" if entity_name else "") + ".")

    elif isinstance(value, int) and not isinstance(value, bool):

        #
        int32_limits = np.iinfo(np.int32)

        if not int32_limits.min <= value <= int32_limits.max:
            raise TypeError(f"Value {value} must fit into signed 32-bit integer" +
                            (f" when used in entity {entity_name}" if entity_name else "") + ".")

    elif isinstance(value, float):

        #
        pass
