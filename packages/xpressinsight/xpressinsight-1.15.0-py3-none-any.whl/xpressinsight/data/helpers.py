"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2023-2025 Fair Isaac Corporation. All rights reserved.
"""

import sys
from typing import Annotated, List, Optional, Type
import pandas as pd

from .. import entities as xi_entities
from ..entities import BasicType, BASIC_TYPE_VALUE, BASIC_TYPE, BASIC_TYPE_MAP
from .. import polars_shims as pl


#
#
# noinspection PyPep8Naming
# pylint: disable-next=invalid-name
def Scalar(
        *,
        #
        dtype: Type[BasicType[BASIC_TYPE_VALUE]] = None,
        entity_name: str = None,
        #
) -> Type[BASIC_TYPE_VALUE]:
    #
    # noinspection PyUnresolvedReferences
    """
    Creates an annotation for a *scalar* entity to be fetched from another scenario.

    Examples
    --------

    >>> @xi.ScenarioData
    ... class DataFromAnotherScenario:
    ...     # Example where the data type is not given.
    ...     NumFactory: xi.data.Scalar()
    ...     # Example where the data type is explicitly stated.
    ...     IsOn: xi.data.Scalar(dtype=xi.boolean)
    ...     # Example where the entity name is different from the attribute name
    ...     OtherScenarioResult: xi.data.Scalar(entity_name='MyResult')

    Parameters
    ----------
    dtype : Type[BasicType[BASIC_TYPE_VALUE]], optional
        The data type; one of `boolean`, `real`, `integer` or `string`. If given,
        `:fct-ref:`insight.get_scenario_data` will verify the data being fetched is of this type.
    entity_name : str, optional
        The name of the entity to read. If not given, the name of the class attribute will be used as
        the entity name.

    Notes
    -----
    This function returns an `Annotated` type containing the `Scalar` entity object; for example,
    if `xpressinsight` has been imported as `xi`, then `xi.data.Scalar(dtype=xi.integer)` is equivalent to
    `Annotated[int, xi.Scalar(dtype=xi.integer)]`.

    See Also
    --------
    ScenarioData
    AppInterface.get_scenario_data
    Scalar
    """
    entity = xi_entities.Scalar(
        dtype=dtype,
        entity_name=entity_name
    )
    return Annotated[BASIC_TYPE_MAP[entity.dtype], entity]


#
#
# noinspection PyPep8Naming
# pylint: disable-next=invalid-name
def Param(
        *,
        #
        dtype: Type[BasicType[BASIC_TYPE_VALUE]] = xi_entities.string,
        entity_name: Optional[str] = None,
        #
) -> Type[BASIC_TYPE_VALUE]:
    #
    # noinspection PyUnresolvedReferences
    """
    Creates an annotation for a *parameter* entity to be fetched from another scenario.

    Examples
    --------

    >>> @xi.ScenarioData
    ... class DataFromAnotherScenario:
    ...     # Example where the data type is not given.
    ...     NumFactory: xi.data.Param()
    ...     # Example where the data type is explicitly stated.
    ...     IsOn: xi.data.Param(dtype=xi.boolean)
    ...     # Example where the parameter name is different from the attribute name
    ...     OtherScenarioResult: xi.data.Param(entity_name='MyResult')

    Parameters
    ----------
    dtype : Type[BasicType[BASIC_TYPE_VALUE]], default xi.string
        The data type; one of `boolean`, `real`, `integer` or `string`. If not given, 'string' is assumed.
    entity_name : str, optional
        The name of the parameter to read. If not given, the name of the class attribute will be used as
        the parameter name.

    Notes
    -----
    This function returns an `Annotated` type containing the `Param` entity object; for example,
    if `xpressinsight` has been imported as `xi`, then `xi.data.Param(dtype=xi.integer)` is equivalent to
    `Annotated[int, xi.Param(dtype=xi.integer)]`.

    Parameters are stored in the Insight data-model as strings, and can always be fetched as strings regardless
    of their original definition.

    See Also
    --------
    ScenarioData
    AppInterface.get_scenario_data
    Param
    """
    entity = xi_entities.Param(
        dtype=dtype,
        entity_name=entity_name
    )
    return Annotated[BASIC_TYPE_MAP[entity.dtype], entity]


#
#
# noinspection PyPep8Naming
# pylint: disable-next=invalid-name
def Index(
        #
        *,
        dtype: BASIC_TYPE = None,
        entity_name: str = None
        #
) -> Type[pd.Index]:
    #
    # noinspection PyUnresolvedReferences
    """
    Creates an annotation for an *index* entity to be fetched from another scenario and stored as a Pandas Index.

    Examples
    --------
    Example creating an index of integer values.

    >>> MyIndex: xi.data.Index(dtype=xi.integer, entity_name="indexSet")

    Parameters
    ----------
    dtype : BASIC_TYPE, optional
        The data type; one of `boolean`, `integer` or `string`. If given,
        `:fct-ref:`insight.get_scenario_data` will verify the data being fetched is of this type.
    entity_name : str, optional
        The name of the entity to read. If not given, the name of the class attribute will be used as
        the entity name.

    Notes
    -----
    This function returns an `Annotated` type containing the `Index` entity object; for example,
    if `xpressinsight` has been imported as `xi`, then `xi.data.Index(dtype=xi.integer)` is equivalent to
    `Annotated[pandas.Index, xi.Index(dtype=xi.integer)]`.

    See Also
    --------
    ScenarioData
    AppInterface.get_scenario_data
    Index
    """
    entity = xi_entities.Index(
        dtype=dtype,
        entity_name=entity_name
    )
    return Annotated[pd.Index, entity]


#
#
# noinspection PyPep8Naming
# pylint: disable-next=invalid-name
def PolarsIndex(
        #
        *,
        dtype: BASIC_TYPE = None,
        entity_name: str = None
        #
) -> Type[pl.Series]:
    #
    # noinspection PyUnresolvedReferences
    """
    Creates an annotation for an *index* entity to be fetched from another scenario and stored as a Polars Series.

    Examples
    --------
    Example creating an index of integer values.

    >>> MyIndex: xi.data.PolarsIndex(dtype=xi.integer, entity_name="indexSet")

    Parameters
    ----------
    dtype : BASIC_TYPE, optional
        The data type; one of `boolean`, `integer` or `string`. If given,
        `:fct-ref:`insight.get_scenario_data` will verify the data being fetched is of this type.
    entity_name : str, optional
        The name of the entity to read. If not given, the name of the class attribute will be used as
        the entity name.

    Notes
    -----
    This function returns an `Annotated` type containing the `Index` entity object; for example,
    if `xpressinsight` has been imported as `xi`, then `xi.data.Index(dtype=xi.integer)` is equivalent to
    `Annotated[pandas.Index, xi.Index(dtype=xi.integer)]`.

    Polars-type entities will only be available if `polars` has been installed in your Python environment.

    See Also
    --------
    ScenarioData
    AppInterface.get_scenario_data
    PolarsIndex
    """
    entity = xi_entities.PolarsIndex(
        dtype=dtype,
        entity_name=entity_name
    )
    return Annotated[pl.Series, entity]


#
#
# noinspection PyPep8Naming
# pylint: disable-next=invalid-name
def Series(
        *,
        dtype: BASIC_TYPE = None,
        entity_name: str = None,
        series_name: str = None,
        index_names: List[str] = None,
        index_types: List[BASIC_TYPE] = None
) -> Type[pd.Series]:
    #
    # noinspection PyUnresolvedReferences
    """
    Creates an annotation for a *Series* entity to be fetched from another scenario.

    Examples
    --------

    >>> Result: xi.data.Series(dtype=xi.real, series_name='Result Array',
    ...                        index_names=['IndexSet1', 'IndexSet2'],)

    Parameters
    ----------
    dtype : BASIC_TYPE, optional
        The data type; one of `boolean`, `real`, `integer` or `string`. If given,
        `:fct-ref:`insight.get_scenario_data` will verify the data being fetched is of this type.
    entity_name : str, optional
        The name of the entity to read. If not given, the name of the class attribute will be used as
        the entity name.
    series_name : str, optional
        The name to use for the values in the resultant series. If not given, the entity name will
        be used.
    index_names : List[str], optional
        The names of the columns to use for the index(es) in the resultant series. If not given, names derived from
        the index entities in the other scenario will be used. If given, the names must be unique and there must be
        one for each index column.
    index_types : List[BASIC_TYPE], optional
        The expected data-types for each of the index columns in the series. If given, you must specify a type
        for each index of this series and `:fct-ref:`insight.get_scenario_data` will verify the index values being
        fetched is of these types.

    Notes
    -----
    This function returns an `Annotated` type containing the `Series` entity object; for example,
    if `xpressinsight` has been imported as `xi`, then `xi.data.Series(index_names=['idx1', 'idx2'], dtype=xi.integer)`
    is equivalent to `Annotated[pandas.Series, xi.Series(index=['idx1', 'idx2'], dtype=xi.integer)]`.

    See Also
    --------
    ScenarioData
    AppInterface.get_scenario_data
    Series
    """
    entity = xi_entities.Series(
        dtype=dtype,
        entity_name=entity_name,
        series_name=series_name,
        index=index_names,
        index_types=index_types
    )
    return Annotated[pd.Series, entity]


class Column(xi_entities.Column):
    #
    # noinspection PyUnresolvedReferences
    """
    Represent a single column within a *DataFrame* or *PolarsDataFrame* entity that is being fetched from another
    scenario.

    Examples
    --------
    Example of declaring two columns `NumDays` and `NumMonths` which will contain integer values within a DataFrame.

    >>> YearInfoFrame: xi.data.DataFrame(columns=[
    ...     xi.data.Column("NumDays", dtype=xi.integer)
    ...     xi.data.Column("NumMonths", dtype=xi.integer)
    ... ])

    The entity name of the column is assumed to be the DataFrame name and column name, joined by an underscore
    (e.g. `YearInfoFrame_NumDays` and `YearInfoFrame_NumMonths` in the above example), unless a different value is
    passed in the `entity_name` attribute.
    """

    # noinspection PyShadowingBuiltins
    def __init__(
            self,
            name: str,
            dtype: Type[BasicType[BASIC_TYPE_VALUE]] = None,
            *,
            default: BASIC_TYPE_VALUE = None,
            entity_name: str = None,
    ):
        """
        Initializes `Column`.

        Parameters
        ----------
        name : str
            The name of the column.
        dtype : BASIC_TYPE, optional
            The data type; one of `boolean`, `real`, `integer` or `string`. If given,
            `:fct-ref:`insight.get_scenario_data` will verify the data being fetched is of this type.
        default : Union[str, bool, int, float], optional
            The value to insert into any cells of this column that do not have a value when the DataFrame
            is loaded from the Insight scenario; optional. If specified, must be a value of the appropriate type for
            the `dtype` of this entity (e.g. a `str` if `dtype` is `string`).
        entity_name : str, optional
            The name of the entity to read. If not given, a name will be constructed from the data frame name and
            the column name.
        """
        super().__init__(
            name=name,
            dtype=dtype,
            default=default,
            entity_name=entity_name
        )


#
#
# noinspection PyPep8Naming
# pylint: disable-next=invalid-name
def DataFrame(
        columns: List[Column],
        *,
        index_names: List[str] = None,
        index_types: List[BASIC_TYPE] = None
) -> Type[pd.DataFrame]:
    #
    # noinspection PyUnresolvedReferences
    """
    Creates an annotation for a *DataFrame* entity to be fetched from another scenario and stored in a Pandas
    DataFrame.

    Examples
    --------
    Example declaring a data frame `MixedTable` which has three columns.

    >>> MixedTable: xi.data.DataFrame(index='Years', columns=[
    ...     xi.data.Column("IntCol", dtype=xi.integer, default=-1),
    ...     xi.data.Column("StrCol", dtype=xi.string),
    ...     xi.data.Column("ResultCol", dtype=xi.real)
    ... ])

    Parameters
    ----------
    columns : Union[Column, List[Column]]
        The columns which make up this data frame.
    index_names : List[str], optional
        The names of the columns to use for the index(es) of the data being read. If not given, names derived from
        the index entities in the other scenario will be used. If given, the names must be unique and there must be
        one for each index column.
    index_types : List[BASIC_TYPE], optional
        The expected data-types for each of the index(es) of the data being read. If given, you must specify a type
        for each index of this series and :fct-ref:`AppInterface.get_scenario_data` will verify the index values being
        fetched is of these types.

    Notes
    -----
    This function returns an `Annotated` type containing the `DataFrame` entity object; for example,
    if `xpressinsight` has been imported as `xi`, then
    `xi.data.DataFrame(index_names=['idx'], columns=[xi.data.Column("c1", dtype=xi.integer)])` is equivalent to
    `Annotated[pandas.DataFrame, xi.DataFrame(index=['idx'], columns=[xi.Column("c1", dtype=xi.integer)])]`.

    See Also
    --------
    Column
    """
    entity = xi_entities.DataFrame(
        index=index_names,
        index_types=index_types,
        columns=columns
    )
    return Annotated[pd.DataFrame, entity]


#
#
# noinspection PyPep8Naming
# pylint: disable-next=invalid-name
def PolarsDataFrame(
        columns: List[Column],
        *,
        index_names: List[str] = None,
        index_types: List[BASIC_TYPE] = None
) -> Type[pl.DataFrame]:
    #
    # noinspection PyUnresolvedReferences
    """
    Creates an annotation for a *PolarsDataFrame* entity to be fetched from another scenario and stored in a Polars
    DataFrame.

    Examples
    --------
    Example declaring a data frame `MixedTable` which has three columns.

    >>> MixedTable: xi.data.PolarsDataFrame(index='Years', columns=[
    ...     xi.data.Column("IntCol", dtype=xi.integer, default=-1),
    ...     xi.data.Column("StrCol", dtype=xi.string),
    ...     xi.data.Column("ResultCol", dtype=xi.real)
    ... ])

    Parameters
    ----------
    columns : Union[Column, List[Column]]
        The columns which make up this data frame.
    index_names : List[str], optional
        The names of the columns to use for Insight index(es) of the data being read. If not given, names derived from
        the index entities in the other scenario will be used. If given, the names must be unique and there must be
        one for each index.
    index_types : List[BASIC_TYPE], optional
        The expected data-types for each of the Insight index(es) of the data being read. If given, you must specify a
        type for each index of this series and `:fct-ref:`insight.get_scenario_data` will verify the index values being
        fetched is of these types.

    Notes
    -----
    This function returns an `Annotated` type containing the `PolarsDataFrame` entity object; for example,
    if `xpressinsight` has been imported as `xi`, then
    `xi.data.PolarsDataFrame(index_names=['idx'], columns=[xi.data.Column("c1", dtype=xi.integer)])` is equivalent to
    `Annotated[polars.DataFrame, xi.PolarsDataFrame(index=['idx'], columns=[xi.Column("c1", dtype=xi.integer)])]`.

    Polars-type entities will only be available if `polars` has been installed in your Python environment.

    See Also
    --------
    Column
    """
    entity = xi_entities.PolarsDataFrame(
        index=index_names,
        index_types=index_types,
        columns=columns
    )
    return Annotated[pl.DataFrame, entity]
