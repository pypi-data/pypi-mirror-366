"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Define the DataFrame entity type and associated classes.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2025 Fair Isaac Corporation. All rights reserved.
"""
from abc import ABC
from copy import deepcopy
from typing import Optional, Type, Union, List, Tuple, Mapping, Any, Iterable
import sys

import pandas as pd

from .basic_types import (BasicType, BASIC_TYPE, BASIC_TYPE_VALUE, SCALAR_DEFAULT_VALUES, check_basic_type_value,
                          check_type_np, check_type_pl)
from .entity import Entity, Hidden, Manage, EntityBase
from .index import Indexed, IndexedPandas, IndexBase, check_polars_index_type_value, report_duplicates_found
from ..type_checking import validate_list
from .. import polars_shims as pl

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override


class Column(Entity):
    """
    Represent a single column within a *DataFrame* or *PolarsDataFrame* entity. Outside the Python model (e.g. VDL,
    Tableau), the column will be represented as a separate entity whose name combines the names of the DataFrame and
    the Column, concatenated by an underscore, i.e. `MyDataFrame_MyColumnName`

    Examples
    --------
    Example of declaring two columns `NumDays` and `NumMonths` which will contain integer values within a DataFrame.

    >>> YearInfoFrame: xi.types.DataFrame(index='Years', columns=[
    ...     xi.types.Column("NumDays", dtype=xi.integer,
    ...                     alias="Number of days"),
    ...     xi.types.Column("NumMonths", dtype=xi.integer,
    ...                     alias="Number of years"),
    ... ])

    When accessing the Insight data model from outside the Python app (for example, in VDL or Tableau views, or using
    the Insight REST API), this DataFrame is represented as two entities, `YearInfoFrame_NumDays` and
    `YearInfoFrame_NumMonths`. If values are inserted into these individual column entities outside the Python
    app, it's possible their indexes may not be consistent (e.g. `YearInfoFrame_NumDays` having values for 2003, 2004
    and 2005 while `YearInfoFrame_NumMonths` has values for just 2003 and 2005). In this case, the empty cells in
    each column will be filled in with a default value when the DataFrame is loaded back into Python.

    See Also
    --------
    types.DataFrame
    types.PolarsDataFrame
    """

    #
    #
    # noinspection PyShadowingBuiltins
    # pylint: disable-next=too-many-arguments
    def __init__(
            self,
            name: str,
            dtype: Optional[Type[BasicType[BASIC_TYPE_VALUE]]],
            #
            alias: str = "",
            format: str = "",  # pylint: disable=redefined-builtin
            hidden: Hidden = Hidden.FALSE,
            manage: Manage = Manage.INPUT,
            read_only: bool = False,
            transform_labels_entity: str = "",
            update_after_execution: bool = False,
            *,
            update_keep_result_data: bool = False,
            update_progress: bool = False,
            default: BASIC_TYPE_VALUE = None,
            entity_name: str = None
            #
    ):
        """
        Initializes `Column`.

        Parameters
        ----------
        name : str
            The name of the column.
        dtype : BASIC_TYPE
            The data type.
        alias : str = ""
            Used to provide an alternative name for an entity in the UI.
            The value is used in place of the entity name where appropriate in the UI.
        format : str = ""
            The formatting string used for displaying numeric values.
        hidden : Hidden = Hidden.FALSE
            Indicates whether the UI should hide the entity where appropriate.
        manage : Manage = Manage.INPUT
            How and whether Insight handles an entity. Defines how the system manages the entity data.
        read_only : bool = False
            Whether an entity is readonly. Specifies that the value(s) of the entity cannot be modified. See also
            `hidden`.
        transform_labels_entity : str = ""
            The name of an entity in the schema from which to read labels for values of this entity.
            The type of the index set of the labels entity must match the data type of this entity.
            The data type of the labels entity can be any primitive type.
        update_after_execution : bool = False
            Whether the value of the entity in the scenario is updated with the value of
            the corresponding model entity at the end of the scenario execution.
            If `True` the value of the entity is updated to correspond with the model entity after execution.
        update_keep_result_data : bool = False
            Whether to retain result data when this input entity is updated outside a scenario execution
            (e.g. in a view or a REST API call).
            If `False`, the result data may be deleted when a view or REST API request updates this entity, depending on
            the configuration of :fct-ref:`AppConfig.result_data`.
            If `True`, the result data will not be deleted when this entity is updated.
        update_progress : bool = False
            Whether the value of the entity in the scenario is sent on progress updates.
            If `True` the value of the entity will be written back to the Insight repository when
            :fct-ref:`insight.send_progress_update` is called from an execution mode where the `send_progress`
            attribute is `True`.
        default : Union[str, bool, int, float] = None
            The value to insert into any cells of this column that do not have a value when the DataFrame
            is loaded from the Insight scenario; optional. If specified, must be a value of the appropriate type for
            the `dtype` of this entity (e.g. a `str` if `dtype` is `string`).
        entity_name : str = None
            The name of the entity in the Insight app schema. If not given, use the column name preceded
            by the name of the containing DataFrame and an underscore.

        Notes
        -----
        Parameters before `update_progress` can be specified positionally for reasons of backwards compatibility,
        but it's recommended that you always use named arguments if you're specifying parameters other than `name`,
        `dtype` and `alias`.
        """
        super().__init__(
            dtype=dtype,
            #
            alias=alias,
            format=format,
            hidden=hidden,
            manage=manage,
            read_only=read_only,
            transform_labels_entity=transform_labels_entity,
            update_after_execution=update_after_execution,
            update_keep_result_data=update_keep_result_data,
            update_progress=update_progress,
            entity_name=entity_name
            #
        )
        #
        self.name = name

        if default is not None:
            check_basic_type_value(dtype, default, name)

        self.__default = default

        self.__data_frame: Optional[EntityBase] = None

    def _init_column(self, data_frame: EntityBase):
        """
        Initializes the column to be part of the given frame.
        """
        if self.__data_frame is not None:
            raise TypeError(f'Column "{self.name}" is already part of a frame')

        #
        #
        #
        if isinstance(data_frame, DataFrame) and self.__default is None and self.dtype is not None:
            self.__default = SCALAR_DEFAULT_VALUES[self.dtype]

        self.__data_frame = data_frame

    @property
    def type_hint(self) -> type:
        """
        The target Python type for values in this Insight entity - e.g. the Python target type of an
        `xpressinsight.DataFrame` is a `pandas.DataFrame`.
        """
        #
        raise TypeError("A Column does not have a type hint")

    @property
    def _data_frame(self) -> EntityBase:
        """
        Reference to the data-frame in which this column exists.
        """
        if self.__data_frame is None:
            raise TypeError(f'Column "{self.name}" has not been added to a frame.')
        return self.__data_frame

    @property
    def default(self) -> Optional[Union[str, bool, int, float]]:
        """
        The value used to fill empty cells in this column when the DataFrame is loaded from the Insight
        scenario.
        """
        return self.__default

    @property
    def _default_entity_name(self) -> str:
        return f"{self.__data_frame.name}_{self.name}"

    @property
    def _allow_non_default_entity_name_in_app(self) -> bool:
        #
        return True

    @property
    def index(self) -> Optional[Tuple[IndexBase, ...]]:
        """ Index entities for this entity. """
        return self._data_frame.index

    @property
    def index_names(self) -> Optional[Tuple[str, ...]]:
        """ Index names for this entity. """
        return self._data_frame.index_names

    @property
    def unique_index_names(self) -> Optional[List[str]]:
        """
        Index names, modified so that each is unique. Where an entity is indexed multiple times by the same index,
        duplicate names will be decorated with their index (e.g. ".2", ".3"). This will correspond to the labels
        of the indexes in the actual series or data frame.
        """
        return self._data_frame.unique_index_names

    @property
    def index_types(self) -> Optional[Tuple[BASIC_TYPE, ...]]:
        """ Index types for this series. """
        return self._data_frame.index_types


class DataFrameBase(EntityBase, Indexed, ABC):
    """
    Abstract base class for entities that comprise multiple columns with a shared index; the shared index can be a
    single or multiple index-type entities.

    See Also
    --------
    DataFrame
    PolarsDataFrame
    """

    def __init__(
            self,
            index: Optional[Union[str, List[str]]],
            columns: Union[Column, List[Column]],
            *,
            index_types: List[Type[BasicType]] = None
    ):
        """
        Initializes `DataFrameBase`.

        Parameters
        ----------
        index : Optional[Union[str, List[str]]] = None
            The name of the index to use, or list of names for multiple indices. Each entry must be the name
            of an `Index` or `PolarsIndex` type entity within the app.
            When used in an `AppConfig`-decorated class, this is required and the same index may appear in the
            list multiple times.
            When used in a `ScenarioData`-decorated class, this is optional if given, the names must be unique and
            there must be one for each index column. If not specified, names derived from the index entities in the
            source scenario will be used.
        columns : Union[Column, List[Column]]
            The columns which make up this data frame.
        index_types : Optional[List[BASIC_TYPE]] = None
            The types of the columns to use for the index(es) in the resultant series.
            Only valid for entities in an `ScenarioData`-decorated class, where it is optional.
        """
        EntityBase.__init__(self)
        Indexed.__init__(
            self,
            index=index,
            index_types=index_types
        )
        self.__columns = validate_list(self, 'columns', Column, 'xpressinsight.Column', deepcopy(columns))
        for col in self.__columns:
            col._init_column(self)

    def _init_app_entity(self, entities: Mapping[str, EntityBase]):
        EntityBase._init_app_entity(self, entities)
        Indexed._init_app_entity(self, entities)

    def _check_valid_app_entity(self):
        EntityBase._check_valid_app_entity(self)
        Indexed._check_valid_app_entity(self)

        for col in self.columns:
            col._check_valid_app_entity()

    def _check_valid_scenario_data_entity(self):
        EntityBase._check_valid_scenario_data_entity(self)
        Indexed._check_valid_scenario_data_entity(self)

        for col in self.columns:
            col._check_valid_scenario_data_entity()

    @property
    def columns(self) -> Tuple[Column, ...]:
        """ Columns in this DataFrame. """
        return self.__columns

    @property
    def update_progress(self) -> bool:
        """ Check whether DataFrame has any columns where the `update_progress` attribute is `True`. """
        return any(column.update_progress for column in self.columns)

    def is_managed(self, manage: Manage) -> bool:
        """ Check whether the DataFrame has a column that is managed as the given management type. """
        return any(column.is_managed(manage) for column in self.columns)

    @property
    def _has_result_values(self) -> bool:
        return any(col.manage == Manage.RESULT for col in self.columns)

    @property
    def _has_keep_result_data_values(self) -> bool:
        return any(col.update_keep_result_data for col in self.columns)


class DataFrame(DataFrameBase, IndexedPandas):
    """
    The configuration of a *DataFrame* entity, which is a group of columns with a shared index, stored as a
    Pandas DataFrame.  Use the helper function `xpressinsight.types.DataFrame` to declare a
    DataFrame entity in an app, rather than instantiating `xpressinsight.DataFrame` directly.

    Notes
    -----
    In older versions of `xpressinsight`, it was possible to use the `DataFrame` as the annotation for an entity.
    This syntax is now deprecated and should not be used in new apps; it will not be supported in Python 3.12 and
    above.

    See Also
    --------
    types.DataFrame
    types.Index
    Column
    """

    def __init__(
            self,
            index: Optional[Union[str, List[str]]],
            columns: Union[Column, List[Column]],
            *,
            index_types: List[Type[BasicType]] = None
    ):
        """
        Initializes `DataFrame`.

        Parameters
        ----------
        index : Union[str, List[str]], optional
            The name of the index to use, or list of names for multiple indices. Each entry must be the name
            of an `Index` or `PolarsIndex` type entity within the app.
            When used in an `AppConfig`-decorated class, this is required and the same index may appear in the
            list multiple times.
            When used in a `ScenarioData`-decorated class, this is optional if given, the names must be unique and
            there must be one for each index column. If not specified, names derived from the index entities in the
            source scenario will be used.
        columns : Union[Column, List[Column]]
            The columns which make up this data frame.
        index_types : List[BASIC_TYPE], optional
            The types of the columns to use for the index(es) in the resultant series.
            Only valid for entities in an `ScenarioData`-decorated class, where it is optional.
        """
        super().__init__(index=index, columns=columns, index_types=index_types)

    @property
    def type_hint(self) -> type:
        """
        The target Python type for values in this Insight entity - e.g. the Python target type of an
        `xpressinsight.Series` is a `pandas.Series`.
        """
        return pd.DataFrame

    @override
    def check_value(self, value: Any,
                    columns: Iterable[Column] = None,
                    *,
                    allow_duplicate_indices: Optional[bool] = None):
        """ Verifies that the given value can be used as the value of an entity of this type, considering
            only the given subset of columns (if specified; all columns if not). """
        #
        if not isinstance(value, pd.DataFrame):
            raise TypeError(f"""
            Problem with entity "{self.name}":
                Expected: pandas DataFrame
                Actual: {type(value)}.
            """)

        #
        self._check_valid_index(value, allow_duplicate_indices=allow_duplicate_indices)

        for column in (columns or self.columns):
            if column.name not in value.columns:
                raise TypeError(f"Missing column '{column.name}' in DataFrame '{self.name}'")

            if column.dtype:
                check_type_np(
                    value.loc[:, column.name].values,
                    column.dtype,
                    f"{self.name}.{column.name}"
                )


class PolarsDataFrame(DataFrameBase):
    """
    The configuration of a *PolarsDataFrame* entity, which is a group of columns with a shared index, represented as a
    Polars DataFrame.  Use the helper function `xpressinsight.types.PolarsDataFrame` to declare a
    DataFrame entity in an app, rather than instantiating `xpressinsight.PolarsDataFrame` directly.

    Notes
    -----
    As Polars frames are not indexed, indexes declared in the Insight schema are represented as additional columns
    of values in the Polars DataFrame. The uniqueness of the index values will be verified when the data is saved
    at the end of the scenario.

    Polars-type entities will only be available if `polars` has been installed in your Python environment.

    See Also
    --------
    types.DataFrame
    types.Index
    Column
    """

    def __init__(
            self,
            index: Optional[Union[str, List[str]]],
            columns: Union[Column, List[Column]],
            *,
            index_types: List[Type[BasicType]] = None
    ):
        """
        Initializes `PolarsDataFrame`.

        Parameters
        ----------
        index : Union[str, List[str]], optional
            The name of the index to use, or list of names for multiple indices. Each entry must be the name
            of an `Index` or `PolarsIndex` type entity within the app.
            When used in an `AppConfig`-decorated class, this is required and the same index may appear in the
            list multiple times.
            When used in a `ScenarioData`-decorated class, this is optional if given, the names must be unique and
            there must be one for each index column. If not specified, names derived from the index entities in the
            source scenario will be used.
        columns : Union[Column, List[Column]]
            The columns which make up this data frame.
        index_types : List[BASIC_TYPE], optional
            The types of the columns to use for the index(es) in the resultant series.
            Only valid for entities in an `ScenarioData`-decorated class, where it is optional.
        """
        pl.check_polars_available()
        super().__init__(index=index, columns=columns, index_types=index_types)

    @property
    def type_hint(self) -> type:
        """
        The target Python type for values in this Insight entity - e.g. the Python target type of an
        `xpressinsight.PolarsDataFrame` is a `polars.DataFrame`.
        """
        return pl.DataFrame

    def _check_valid_index(self, value: pl.DataFrame, allow_duplicate_indices: Optional[bool]):
        """ Check the types of the indexes of the Polars data-frame. """
        if self.index_types:
            index_names = self.unique_index_names
            if not index_names:
                #
                index_names = value.columns[:len(self.index_types)]

            for idx_id, (idx_name, idx_dtype) in enumerate(zip(index_names, self.index_types), start=1):
                if idx_name not in value.columns:
                    raise TypeError(f"""
                    Problem with entity "{self.name}":
                        Expected: polars DataFrame with column {idx_name}
                        Actual: {value.columns}.
                    """)
                check_polars_index_type_value(value.get_column(idx_name), idx_dtype,
                                              f'index {idx_id} ("{idx_name}") of entity "{self.name}"')

            #
            #
            if allow_duplicate_indices is not True and value.height > 0:
                duplicate_index_counts = (value.lazy()
                                          .group_by(list(index_names))
                                          .len()
                                          .filter(pl.col("len").gt(1))
                                          .collect())
                if duplicate_index_counts.height > 0:
                    duplicate_index_tuple = ', '.join(str(duplicate_index_counts.item(0, idx))
                                                      for idx in self.unique_index_names)
                    if duplicate_index_counts.height > 1:
                        and_others = f" and {duplicate_index_counts.height - 1} others"
                    else:
                        and_others = ''
                    report_duplicates_found(allow_duplicate_indices=allow_duplicate_indices, message=f"""
                        Problem with entity "{self.name}":
                            Expected: polars DataFrame with unique index tuples
                            Actual: Duplicate entries for index ({duplicate_index_tuple}){and_others}.
                        """)

    @override
    def check_value(self, value: Any,
                    columns: Iterable[Column] = None,
                    *,
                    allow_duplicate_indices: Optional[bool] = None):
        """ Verifies that the given value can be used as the value of an entity of this type, considering
            only the given subset of columns (if specified; all columns if not). """
        #
        if not isinstance(value, pl.DataFrame):
            raise TypeError(f"""
            Problem with entity "{self.name}":
                Expected: polars DataFrame
                Actual: {type(value)}.
            """)

        #
        self._check_valid_index(value, allow_duplicate_indices=allow_duplicate_indices)

        for column in (columns or self.columns):
            if column.name not in value.columns:
                raise TypeError(f"Missing column '{column.name}' in DataFrame '{self.name}'")

            if column.dtype:
                check_type_pl(
                    value.get_column(column.name),
                    column.dtype,
                    f"{self.name}.{column.name}"
                )
