"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    'Entities' subpackage defines the various entity classes.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""

from .basic_types import (
    BASIC_TYPE,
    BASIC_TYPE_VALUE,
    BASIC_PANDAS_DTYPE_MAP,
    BASIC_POLARS_DTYPE_MAP,
    BASIC_TYPE_MAP,
    ALL_BASIC_TYPE,
    BasicType,
    boolean,
    integer,
    real,
    string,
    SCALAR_DEFAULT_VALUES
)
from .entity import (
    Manage,
    Hidden,
    UnexpectedEntityTypeError,
    Entity,
    EntityBase,
    ENTITY_CLASS_NAMES
)
from .utils import (
    get_non_composed_entities,
    get_non_composed_entities_from_names
)
from .scalar import ScalarBase, Scalar, Param
from .data_frame import Column, DataFrame, DataFrameBase, PolarsDataFrame
from .series import Series
from .index import Index, IndexBase, Indexed, IndexedPandas, PolarsIndex
