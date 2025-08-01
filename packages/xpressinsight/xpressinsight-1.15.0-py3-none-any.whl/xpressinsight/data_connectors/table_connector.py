"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2025 Fair Isaac Corporation. All rights reserved.
"""

import sys
from abc import abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, Union, Type, List, Callable, Iterable, Optional

import numpy as np
import pandas as pd
import pyarrow as pa

from .. import entities as xi_types
from .. import polars_shims as pl
from .data_connector import DataConnector, SingleValueDict
from ..entities import UnexpectedEntityTypeError
from ..entities.basic_types import PANDAS_DTYPE_TYPES_FOR_INSIGHT_TYPES
from ..entities_config import EntitiesContainer
from ..slow_tasks_monitor import SlowTasksMonitor
from ..type_checking import python_int_to_bool


#
#
#
TABLE_PREFIX_ENTITY = "ENTITY_"

SPType = Union[Type[xi_types.Scalar], Type[xi_types.Param]]

ERR_ABSTRACT = "Cannot call abstract method of base class."


class TableConnector(DataConnector):
    """
    TableConnector - DataConnector implementation in which all the entity data is read from/written to flat tables.
    """

    def __init__(self, data_container: EntitiesContainer, fetch_individual_series=True,
                 slow_tasks_monitor: Optional[SlowTasksMonitor] = None,
                 allow_duplicate_indices: Optional[bool] = None,
                 single_parameters_table=False):
        super().__init__(data_container)
        self._data_container = data_container
        self._verbose: bool = False
        #
        #
        self._fetch_individual_series: bool = fetch_individual_series
        #
        self._shared_parameters_table: bool = single_parameters_table
        self._slow_tasks_monitor = slow_tasks_monitor or SlowTasksMonitor.default()
        self._allow_duplicate_indices = allow_duplicate_indices

    @staticmethod
    def _encode_identifier(ident: str) -> str:
        """
        Encode a valid identifier (table or column name) so that it can be used in a case-insensitive environment
        (e.g. as an NTFS file name or in an SQL database).
        """
        tail = (
            np.packbits([int(c.isupper()) for c in ident], bitorder="little").tobytes().hex()
        )
        return f"{ident}_{tail}"

    @staticmethod
    def _decode_identifier(encoded_ident: str) -> str:
        """
        Decode a valid identifier returned by _encode_identifier
        """
        tail_idx = encoded_ident.rindex('_')
        tail = encoded_ident[(tail_idx+1):]
        #
        case_bits = np.unpackbits(np.frombuffer(bytes.fromhex(tail), dtype=np.uint8), bitorder="little")
        return ''.join(c.upper() if is_upper else c.lower()
                       for (c, is_upper) in zip(encoded_ident[:tail_idx], case_bits))

    @abstractmethod
    def _get_export_type(self, src_type: Type[xi_types.BasicType]) -> pa.DataType:
        raise RuntimeError(ERR_ABSTRACT)

    @abstractmethod
    def _get_polars_export_type(self, src_type: Type[xi_types.BasicType]) -> pl.DataType:
        raise RuntimeError(ERR_ABSTRACT)

    @staticmethod
    def _get_import_type(dtype, entity_name: str) -> PANDAS_DTYPE_TYPES_FOR_INSIGHT_TYPES:
        """ Get the preferred type for a column of the given Pandas or XpressInsight dtype.  The given entity_name
            will be used in an error message if the column type cannot be recognized. """
        if isinstance(dtype, type) and issubclass(dtype, xi_types.BasicType):
            return xi_types.BASIC_PANDAS_DTYPE_MAP[dtype]

        if pd.api.types.is_integer_dtype(dtype):
            return xi_types.BASIC_PANDAS_DTYPE_MAP[xi_types.integer]
        if pd.api.types.is_bool_dtype(dtype):
            return xi_types.BASIC_PANDAS_DTYPE_MAP[xi_types.boolean]
        if pd.api.types.is_float_dtype(dtype):
            return xi_types.BASIC_PANDAS_DTYPE_MAP[xi_types.real]
        if pd.api.types.is_string_dtype(dtype):
            return xi_types.BASIC_PANDAS_DTYPE_MAP[xi_types.string]

        raise RuntimeError(f'Unrecognized index type {dtype} for entity "{entity_name}"')

    @abstractmethod
    def _encode_column_name(self, ident: str) -> str:
        raise RuntimeError(ERR_ABSTRACT)

    @abstractmethod
    def _decode_column_name(self, ident: str) -> str:
        raise RuntimeError(ERR_ABSTRACT)

    def _encode_table_name(self, name: str) -> str:
        return TABLE_PREFIX_ENTITY + self._encode_identifier(name)

    def _decode_table_name(self, name: str) -> str:
        if not name.startswith(TABLE_PREFIX_ENTITY):
            raise ValueError(f'"{name} is not an entity table')

        return TableConnector._decode_identifier(name[len(TABLE_PREFIX_ENTITY):])

    def _encode_entity_table_name(self, entity: xi_types.EntityBase) -> str:
        if isinstance(entity, xi_types.Column):
            #
            return self._encode_table_name(entity.entity_name)

        #
        return self._encode_table_name(entity.name)

    @staticmethod
    def _sp_table_name(sp_type: SPType, dtype: Type[xi_types.BasicType]) -> str:
        """Returns the table name"""
        return sp_type.__name__.upper() + "_" + dtype.__name__

    @staticmethod
    def _get_entities(data_container, entity_filter: Callable[[xi_types.Entity], bool] = None
                      ) -> Iterable[xi_types.EntityBase]:
        """
        Get the entities list for the given container.  Error if it doesn't have one.
        If filter is supplied, returns list of entities that pass the filter.
        A DataFrame entity will pass the filter if any of its columns pass the filter.
        """
        if not entity_filter:
            return data_container.get_entities_cfg().entities

        entities: List[xi_types.EntityBase] = []
        for entity in data_container.get_entities_cfg().entities:
            if isinstance(entity, xi_types.DataFrameBase):
                if any(entity_filter(col) for col in entity.columns):
                    entities.append(entity)
            elif entity_filter(entity):
                entities.append(entity)

        return entities

    def _get_empty_index_for_frame_with_undeclared_indices(self, df: pd.DataFrame,
                                                           columns: Iterable[xi_types.Column]) -> pd.Index:
        """ Given an entity which doesn't declare index names, create a suitable empty index from the columns
            of the input frame that do not match entries in the 'columns' array. """
        non_index_column_names = {self._encode_column_name(c.entity_name) for c in columns}
        index_names = [self._decode_column_name(name) for name in df.columns.to_list()
                       if name not in non_index_column_names]
        if len(index_names) == len(df.columns):
            raise ValueError(f"No non-index columns found in data-frame: {df.columns}")

        index_list = [
            pd.Index([],
                     dtype=TableConnector._get_import_type(df[index_name].dtype, entity_name=index_name),
                     name=index_name)
            for index_name in index_names
        ]

        if len(index_list) == 1:
            pd_index = index_list[0]
        else:
            pd_index = pd.MultiIndex.from_product(index_list)

        return pd_index

    def _load_single_values_db(self, prefix: str) -> SingleValueDict:
        """Loads from the database and returns SingleValueDict"""

        assert prefix in ("SCALAR", "PARAM", "META")

        values = {}

        for dtype in xi_types.ALL_BASIC_TYPE:
            table_name = f"{prefix}_{dtype.__name__}"

            if self._has_table(table_name):
                df = self._import_table(table_name)

                if ("Name" not in df.columns) or ("Value" not in df.columns):
                    raise KeyError(f"Table {table_name} must have 'Name' and 'Value' columns, it has {df.columns}.")

                values[dtype] = dict(zip(df["Name"], df["Value"]))
            else:
                values[dtype] = {}

        #
        values[xi_types.boolean] = {
            name: python_int_to_bool(value, name=name)
            for name, value in values[xi_types.boolean].items()
        }

        return values

    @staticmethod
    def _merge_single_value_dicts(dict1: SingleValueDict, dict2: SingleValueDict) -> SingleValueDict:
        """ Returns a SingleValueDict containing all the values from dict2, and any values from dict1 that
            were not in dict2. """
        merged_values = {}
        for dtype in xi_types.ALL_BASIC_TYPE:
            if dtype not in dict1:
                if dtype in dict2:
                    merged_values[dtype] = dict2[dtype]
            elif dtype not in dict2:
                merged_values[dtype] = dict1[dtype]
            else:
                merged_values[dtype] = {**dict1[dtype], **dict2[dtype]}

        return merged_values

    def _save_single_values_db(self, prefix: str, values: SingleValueDict, merge: bool = False):
        """Saves SingleValueDict to the database.  If merge=TRUE is set, combine with existing values from the
           single-values DB """

        assert prefix in ("SCALAR", "PARAM", "META")

        if merge:
            values = TableConnector._merge_single_value_dicts(self._load_single_values_db(prefix), values)

        for dtype in xi_types.ALL_BASIC_TYPE:
            #
            if dtype in values and values[dtype]:
                table_name = f"{prefix}_{dtype.__name__}"

                df = pd.DataFrame(
                    values[dtype].items(), columns=["Name", "Value"]
                ).set_index("Name")
                dtypes = {
                    "Name": self._get_export_type(xi_types.string),
                    "Value": self._get_export_type(dtype),
                }
                self._export_table(df, table_name, dtype=dtypes, data_col_nullable=False)

    def initialize_entities(self, entity_filter: Callable[[xi_types.Entity], bool], overwrite: bool = True) -> None:
        """
        Initializes the values of the entities of the given container that match the given filter, to the
        appropriate default value.
        Raises error if overwrite=False and entity already exists
        """
        for entity in TableConnector._get_entities(self._data_container, entity_filter):
            #
            #
            if entity.name in self._data_container.__dict__ and \
                    not overwrite and not isinstance(entity, xi_types.DataFrameBase):
                raise RuntimeError(f'Entity "{entity.name}" already has a value.')

            if isinstance(entity, xi_types.ScalarBase):
                self._initialize_scalar_or_param(entity)
            elif isinstance(entity, xi_types.Index):
                self._initialize_index(entity)
            elif isinstance(entity, xi_types.PolarsIndex):
                self._initialize_polars_index(entity)
            elif isinstance(entity, xi_types.Series):
                self._initialize_series(entity)
            elif isinstance(entity, xi_types.DataFrame):
                self._initialize_data_frame(entity, [c for c in entity.columns if entity_filter(c)],
                                            overwrite=overwrite)
            elif isinstance(entity, xi_types.PolarsDataFrame):
                self._initialize_polars_data_frame(entity, [c for c in entity.columns if entity_filter(c)],
                                            overwrite=overwrite)
            else:
                raise UnexpectedEntityTypeError(entity)

    def _initialize_scalar_or_param(self, entity: xi_types.ScalarBase) -> None:
        self._data_container.__dict__[entity.name] = entity.default

    def _initialize_index(self, entity: xi_types.Index) -> None:
        self._data_container.__dict__[entity.name] = pd.Index(
            dtype=xi_types.BASIC_PANDAS_DTYPE_MAP[entity.dtype],
            data=[])

    def _initialize_polars_index(self, entity: xi_types.Index) -> None:
        self._data_container.__dict__[entity.name] = pl.Series(
            name=entity.name,
            dtype=xi_types.BASIC_POLARS_DTYPE_MAP[entity.dtype])

    def _initialize_series(self, entity: xi_types.Series) -> None:
        self._data_container.__dict__[entity.name] = pd.Series(
            dtype=xi_types.BASIC_PANDAS_DTYPE_MAP[entity.dtype],
            index=entity._get_empty_index())

    def _initialize_data_frame(self, entity: xi_types.DataFrame, columns: Iterable[xi_types.Column],
                               overwrite: bool) -> None:
        df = self._data_container.__dict__.get(entity.name)
        if df is not None and not isinstance(df, pd.DataFrame):
            raise TypeError(f'Expected entity "{entity.name}" to have type "{pd.DataFrame}", found "{type(df)}"')

        #
        column_names = {c.name for c in columns}
        if df is not None and overwrite and all((col in column_names) for col in df.columns):
            df = None

        #
        #
        if df is None:
            df = pd.DataFrame(index=entity._get_empty_index())

        #
        for col in columns:
            if col.name in df and not overwrite:
                raise RuntimeError(f'Column "{col.name}" of entity "{entity.name}" already exists.')

            #
            df[col.name] = pd.Series([], dtype=xi_types.BASIC_PANDAS_DTYPE_MAP[col.dtype]) \
                               .reindex(index=df.index, copy=False, fill_value=col.default)

        #
        #
        #
        self._data_container.__dict__[entity.name] = df

    def _initialize_polars_data_frame(self, entity: xi_types.PolarsDataFrame, columns: Iterable[xi_types.Column],
                                      overwrite: bool) -> None:
        df = self._data_container.__dict__.get(entity.name)

        if df is not None and not isinstance(df, (pl.LazyFrame, pl.DataFrame)):
            raise TypeError(f'Expected entity "{entity.name}" to have type "{pl.DataFrame}", found "{type(df)}"')

        #
        col_names_to_init = {c.name for c in columns}
        index_names = set(entity.unique_index_names)
        if df is not None and overwrite and all((col in col_names_to_init or col in index_names)
                                                for col in df.columns):
            df = None

        #
        #
        if df is None:
            df = pl.DataFrame({label: pl.Series(label, dtype=xi_types.BASIC_POLARS_DTYPE_MAP[dtype])
                               for (label, dtype) in zip(entity.unique_index_names, entity.index_types)})

        #
        col_init_exprs = {col.name: pl.lit(col.default,
                                           dtype=xi_types.BASIC_POLARS_DTYPE_MAP[col.dtype]).alias(col.name)
                          for col in columns}

        #
        col_names_to_replace = {name for name in df.columns if name in col_names_to_init}
        col_names_to_add = [col.name for col in columns if col.name not in col_names_to_replace]

        if col_names_to_replace and not overwrite:
            raise RuntimeError(f'Column "{col_names_to_replace.pop()}" of entity "{entity.name}" already exists.')

        #
        df = df.lazy().select(
            #
            [(pl.col(name) if name not in col_names_to_replace else col_init_exprs[name]) for name in df.columns] +
            #
            [col_init_exprs[name] for name in col_names_to_add]
        )

        #
        self._data_container.__dict__[entity.name] = df.collect()

    def load_meta(self) -> SingleValueDict:
        return self._load_single_values_db('META')

    def _load_scalars(self, data_container, entities: Iterable[xi_types.ScalarBase], table_prefix: str):
        """
        Given a collection of scalar-type entities, load the values from the given table prefix, where there
        is a table for each value type.
        """
        values_by_type = self._load_single_values_db(table_prefix)

        #
        values: Dict[str, Any] = {}
        for values_of_type in values_by_type.values():
            for (name, value) in values_of_type.items():
                if name in values:
                    raise KeyError(f"Multiple values found for {name} in single-values db")

                values[name] = value

        #
        for entity in entities:
            if entity.entity_name not in values:
                raise ValueError(f"{'Parameter' if entity.dtype == xi_types.Param else 'Scalar'} {entity.entity_name}"
                                 f"{(' (of type ' + entity.dtype.__name__+ ')') if entity.dtype else ''} does not "
                                 f"exist in the data store.")

            value = values[entity.entity_name]

            entity.check_value(value, allow_duplicate_indices=self._allow_duplicate_indices)
            data_container.__dict__[entity.name] = value

    def _load_scalars_from_strings(self, data_container, entities: Iterable[xi_types.ScalarBase], table_name: str):
        """
        Given a collection of scalar-type entities, load the values from a table of strings.
        """
        values_as_strings = self._import_table(table_name).set_index(['Name'])['Value']

        #
        for entity in entities:
            try:
                value_as_string = values_as_strings[entity.entity_name]
            except KeyError as ke:
                raise ValueError(f"{'Parameter' if isinstance(entity, xi_types.Param) else 'Scalar'} {entity.entity_name}"
                                 f" does not exist in the data store.") from ke

            if entity.dtype == xi_types.boolean:
                value = (value_as_string.lower() == 'true')
            elif entity.dtype == xi_types.real:
                value = float(value_as_string)
            elif entity.dtype == xi_types.integer:
                value = int(value_as_string)
            elif entity.dtype == xi_types.string:
                value = value_as_string
            else:
                raise ValueError(f"{'Parameter' if isinstance(entity, xi_types.Param) else 'Scalar'} {entity.entity_name}"
                                 f" has unrecognized type '{entity.dtype}'")

            data_container.__dict__[entity.name] = value

    def _load_index(self, data_container, entity: xi_types.Index):
        """ Load a given Pandas index-type entity into the data container. """
        table_name = self._encode_entity_table_name(entity)
        df = self._import_table(table_name)
        df.columns = [self._decode_column_name(c) for c in df.columns]

        value = df.set_index(entity.name).index
        entity.check_value(value, allow_duplicate_indices=self._allow_duplicate_indices)
        data_container.__dict__[entity.name] = value

    def _load_polars_index(self, data_container, entity: xi_types.PolarsIndex):
        """ Load a given Polars index-type entity into the data container. """
        table_name = self._encode_entity_table_name(entity)
        df = self._import_polars_table(table_name)
        df = df.collect()
        df = df.rename({df.columns[0]: entity.name})
        value = df.get_column(df.columns[0])
        entity.check_value(value, allow_duplicate_indices=self._allow_duplicate_indices)
        data_container.__dict__[entity.name] = value

    def _load_series(self, data_container, entity: xi_types.Series):
        """ Load a given series-type entity into the data container. """
        table_name = self._encode_entity_table_name(entity)
        df = self._import_table(table_name)
        df.columns = [self._decode_column_name(c) for c in df.columns]

        #
        #
        index_names = entity.unique_index_names or \
            [col for col in df.columns if col != entity.series_name]

        value = df.set_index(index_names)[entity.series_name]
        entity.check_value(value, allow_duplicate_indices=self._allow_duplicate_indices)
        data_container.__dict__[entity.name] = value

    @staticmethod
    def _get_column_default_value(col: xi_types.Column, series: pd.Series) -> Optional[Union[bool, int, str, float]]:
        """ Determine the default value to use for the given Pandas column. """
        #
        if col.default is not None:
            return col.default

        #
        assert col.dtype is None

        #
        if pd.api.types.is_bool_dtype(series.dtype):
            return xi_types.SCALAR_DEFAULT_VALUES[xi_types.boolean]

        if pd.api.types.is_float_dtype(series.dtype):
            return xi_types.SCALAR_DEFAULT_VALUES[xi_types.real]

        if pd.api.types.is_string_dtype(series.dtype):
            return xi_types.SCALAR_DEFAULT_VALUES[xi_types.string]

        if pd.api.types.is_integer_dtype(series.dtype):
            return xi_types.SCALAR_DEFAULT_VALUES[xi_types.integer]

        return None  #

    def _import_data_frame_from_single_table(self, entity: xi_types.DataFrame,
                                             columns: Iterable[xi_types.Column]) -> pd.DataFrame:
        """ Import a data frame from a single, multi-column table. """
        table_name = self._encode_entity_table_name(entity)
        df = self._import_table(table_name)

        #
        if entity.index_names:
            encoded_index_names = [self._encode_column_name(name) for name in entity.unique_index_names]

        #
        else:
            non_index_column_names = {self._encode_column_name(c.name) for c in columns}
            encoded_index_names = [name for name in df.columns.to_list()
                                   if name not in non_index_column_names]

        #
        df.set_index(encoded_index_names, inplace=True)

        #
        return df

    def _import_data_frame_from_multiple_tables(self, entity: xi_types.DataFrame,
                                                columns: Iterable[xi_types.Column]) -> pd.DataFrame:
        """ Import a data frame from multiple tables, each containing a single series. """
        #
        if entity.index_names:
            #
            index_rename_map = {
                self._encode_column_name(index_name): index_name for index_name in entity.unique_index_names
            }
            pd_index = entity._get_empty_index()
            index_names = pd_index.names

        else:
            #
            #
            index_rename_map = {}
            pd_index = None
            index_names = None

        #
        data: dict[str, pd.Series] = {}
        for c in columns:
            table_name = self._encode_entity_table_name(c)
            encoded_data_col_name = self._encode_column_name(c.entity_name)

            df = self._import_table(table_name)

            #
            if pd_index is None:
                pd_index = self._get_empty_index_for_frame_with_undeclared_indices(df, columns)
                index_names = pd_index.names
                index_rename_map = {
                    index_name: self._decode_column_name(index_name) for index_name in index_names
                }

            if index_rename_map:
                df.rename(columns=index_rename_map, inplace=True)

            #
            df.set_index(index_names, inplace=True)

            #
            data[c.name] = df[encoded_data_col_name]

        #
        for c in columns:
            pd_index = pd_index.union(data[c.name].index)

        #
        #
        #
        for c in columns:
            data[c.name] = data[c.name].reindex(pd_index,
                                                fill_value=TableConnector._get_column_default_value(c, data[c.name]))

        #
        df_full = pd.DataFrame(data, index=pd_index)
        return df_full

    def _load_data_frame(self, data_container, entity: xi_types.DataFrame, columns: Iterable[xi_types.Column]) -> None:
        if self._fetch_individual_series:
            df = self._import_data_frame_from_multiple_tables(entity, columns)
        else:
            df = self._import_data_frame_from_single_table(entity, columns)

        #
        unique_index_names = entity.unique_index_names
        if unique_index_names:
            df.index.rename(list(unique_index_names)[0] if len(unique_index_names) == 1 else unique_index_names,
                            inplace=True)

        #
        column_rename_map = {
            df_col_name: entity_col.name for (df_col_name, entity_col) in zip(df.columns, columns)
        }
        df.rename(columns=column_rename_map, inplace=True)

        #
        #
        if entity.name in self._data_container.__dict__:
            df_org = self._data_container.__dict__[entity.name]

            if isinstance(df_org, pd.DataFrame):
                for col_label, col in df_org.items():
                    #
                    if col_label not in df.columns:
                        #
                        #
                        #
                        #
                        df[col_label] = col

        #
        entity.check_value(df, columns=columns, allow_duplicate_indices=self._allow_duplicate_indices)
        data_container.__dict__[entity.name] = df

    def _import_polars_data_frame_from_single_table(self, entity: xi_types.PolarsDataFrame,
                                                    columns: Iterable[xi_types.Column]) -> pl.LazyFrame:
        """ Import a data frame from a single, multi-column table. """
        table_name = self._encode_entity_table_name(entity)
        df = self._import_polars_table(table_name)

        #
        index_names = entity.unique_index_names
        if index_names:
            encoded_index_names = [self._encode_column_name(label) for label in index_names]
        else:
            #
            encoded_index_names = df.columns[:len(df.columns)-len(columns)]
            index_names = [self._decode_column_name(label) for label in encoded_index_names]

        column_rename_map = dict(zip(encoded_index_names, index_names))
        for c in columns:
            column_rename_map[self._encode_column_name(c.name)] = c.name

        #
        return df.rename(mapping=column_rename_map)

    def _import_polars_data_frame_from_multiple_tables(self, entity: xi_types.PolarsDataFrame,
                                                       columns: Iterable[xi_types.Column]) -> pl.LazyFrame:
        """ Import a data frame from multiple tables, each containing a single series. """
        #
        df_full : Optional[pl.LazyFrame] = None
        index_names = entity.unique_index_names
        encoded_index_names = [self._encode_column_name(label) for label in index_names] if index_names else None
        for c in columns:
            table_name = self._encode_entity_table_name(c)
            df_column = self._import_polars_table(table_name)

            #
            #
            if not encoded_index_names:
                encoded_index_names = df_column.columns[:len(df_column.columns)-1]
            if not index_names:
                index_names = [self._decode_column_name(label) for label in encoded_index_names]
            encoded_data_col_name = self._encode_column_name(c.entity_name)

            #
            column_rename_map = dict(zip(encoded_index_names, index_names))
            column_rename_map[encoded_data_col_name] = c.name
            df_column = df_column.rename(mapping=column_rename_map)

            if df_full is None:
                #
                df_full = df_column
            else:
                #
                df_full = df_full.join(other=df_column, on=index_names, how='outer_coalesce')

        #
        df_full = df_full.with_columns(
            [pl.col(c.name).fill_null(value=c.default)
             for c in columns
             if c.default is not None]
        )

        return df_full

    def _load_polars_data_frame(self, data_container, entity: xi_types.PolarsDataFrame,
                                columns: Iterable[xi_types.Column]) -> None:
        if self._fetch_individual_series:
            df = self._import_polars_data_frame_from_multiple_tables(entity, columns)
        else:
            df = self._import_polars_data_frame_from_single_table(entity, columns)

        #
        #
        #
        #
        #

        #
        df = df.collect()
        entity.check_value(df, columns=columns, allow_duplicate_indices=self._allow_duplicate_indices)
        data_container.__dict__[entity.name] = df

    def load_entities(self, entity_filter: Callable[[xi_types.Entity], bool]) -> None:
        """
        Load the given entities into the given data container into the given data store.
        """
        with self._connect():
            param_entities: List[xi_types.Param] = []
            scalar_entities: List[xi_types.Scalar] = []
            for entity in TableConnector._get_entities(self._data_container, entity_filter):
                with self._slow_tasks_monitor.task(f'Loading data into entity `{entity.name}`'):
                    if isinstance(entity, xi_types.Param):
                        #
                        param_entities.append(entity)

                    elif isinstance(entity, xi_types.Scalar):
                        #
                        scalar_entities.append(entity)

                    elif isinstance(entity, xi_types.Index):
                        self._load_index(self._data_container, entity)

                    elif isinstance(entity, xi_types.PolarsIndex):
                        self._load_polars_index(self._data_container, entity)

                    elif isinstance(entity, xi_types.Series):
                        self._load_series(self._data_container, entity)

                    elif isinstance(entity, xi_types.DataFrame):
                        self._load_data_frame(self._data_container, entity,
                                              [col for col in entity.columns if entity_filter(col)])

                    elif isinstance(entity, xi_types.PolarsDataFrame):
                        self._load_polars_data_frame(self._data_container, entity,
                                                     [col for col in entity.columns if entity_filter(col)])

                    else:
                        raise UnexpectedEntityTypeError(entity)

            #
            if param_entities:
                with self._slow_tasks_monitor.task(f'Loading data into parameter entities'):
                    if self._shared_parameters_table:
                        self._load_scalars_from_strings(self._data_container, param_entities, 'PARAM')
                    else:
                        self._load_scalars(self._data_container, param_entities, 'PARAM')
            if scalar_entities:
                with self._slow_tasks_monitor.task(f'Loading data into scalar entities'):
                    self._load_scalars(self._data_container, scalar_entities, 'SCALAR')

    @abstractmethod
    def _does_db_exist(self) -> bool:
        """ Returns True iff data repository directory exists. """
        raise RuntimeError(ERR_ABSTRACT)

    @abstractmethod
    def _check_db_exists(self):
        raise RuntimeError(ERR_ABSTRACT)

    @abstractmethod
    def _has_table(self, table_name: str) -> bool:
        """ Returns True iff given table exists in data repository. """
        raise RuntimeError(ERR_ABSTRACT)

    @abstractmethod
    def _import_table(self, table_name: str) -> pd.DataFrame:
        """ Import named table to a Pandas DataFrame."""
        raise RuntimeError(ERR_ABSTRACT)

    @abstractmethod
    def _export_table(self, df: Union[pd.DataFrame, pd.Series], table_name: str, dtype: Dict[str, pa.DataType],
                      index: bool = True, data_col_nullable: bool = False) -> None:
        """ Export Pandas data-frame or series to named table. """
        raise RuntimeError(ERR_ABSTRACT)

    @abstractmethod
    def _import_polars_table(self, table_name: str) -> pl.LazyFrame:
        """ Import named table to a Polars DataFrame. """
        raise RuntimeError(ERR_ABSTRACT)

    @abstractmethod
    def _export_polars_table(self, df: Union[pl.DataFrame, pl.LazyFrame], table_name: str,
                             dtypes: Dict[str, pl.DataType]) -> None:
        """ Export Polars data-frame to named table. """
        raise RuntimeError(ERR_ABSTRACT)

    def _save_scalars(self, entity_values: SingleValueDict, table_prefix: str) -> None:
        """
        Given a collection of values from scalar-type entities (Scalar or Param), save these values to the given
        table prefix.
        The caller will already have populated `entity_values` with the values for the entities they want to save.
        This retains any existing scalar values not part of the entity_values dictionary.
        """
        self._save_single_values_db(table_prefix, entity_values, merge=True)

    def _save_index(self, entity: xi_types.Index, value: pd.Index) -> None:
        """ Write the value of the given index entity to the data store. """
        ser = value.to_series()
        ser.name = self._encode_column_name(entity.name)
        dtype = {ser.name: self._get_export_type(entity.dtype)}
        table_name = self._encode_entity_table_name(entity)

        self._export_table(ser, table_name, index=False, dtype=dtype, data_col_nullable=False)

    def _save_polars_index(self, entity: xi_types.PolarsIndex, value: pl.Series) -> None:
        """ Write the value of the given index entity to the data store. """
        table_name = self._encode_entity_table_name(entity)
        column_name = self._encode_column_name(entity.name)
        df = pl.DataFrame({column_name: value}).lazy()
        dtypes = {column_name: self._get_polars_export_type(entity.dtype)}
        self._export_polars_table(df, table_name, dtypes=dtypes)

    def _save_series(self, entity: xi_types.Series, value: pd.Series) -> None:
        """ Write the value of the given series to the data store. """
        original_name = value.name
        original_index_names = value.index.names
        try:
            enc_col_name = self._encode_column_name(entity.name)
            value.name = enc_col_name
            value.index.names = [self._encode_column_name(index_label) for index_label in entity.unique_index_names]
            dtype = {
                self._encode_column_name(index_label): self._get_export_type(ind.dtype)
                for (index_label, ind) in zip(entity.unique_index_names, entity.index)
            }
            dtype[enc_col_name] = self._get_export_type(entity.dtype)
            table_name = self._encode_entity_table_name(entity)

            self._export_table(value, table_name, dtype=dtype, data_col_nullable=True)
        finally:
            value.name = original_name
            value.index.names = original_index_names

    def _save_data_frame(self, entity: xi_types.DataFrame, value: pd.DataFrame,
                         columns: Iterable[xi_types.Column]) -> None:
        """ Write the value of the given columns of the given data-frame to the data store. """
        if not self._fetch_individual_series:
            #
            #
            #
            raise RuntimeError("Frames may only be stored as one series per table.")

        for c in columns:
            #
            ser = value[c.name]
            original_name = ser.name
            original_index_names = ser.index.names

            try:
                #
                enc_col_name = self._encode_column_name(c.entity_name)
                ser.name = enc_col_name
                ser.index.names = [self._encode_column_name(index_label) for index_label in entity.unique_index_names]
                dtype = {
                    self._encode_column_name(index_label): self._get_export_type(ind.dtype)
                    for (index_label, ind) in zip(entity.unique_index_names, entity.index)
                }
                dtype[enc_col_name] = self._get_export_type(c.dtype)
                table_name = self._encode_entity_table_name(c)

                self._export_table(ser, table_name, dtype=dtype, data_col_nullable=True)
            finally:
                ser.name = original_name
                ser.index.names = original_index_names

    def _save_polars_data_frame(self, entity: xi_types.PolarsDataFrame, value: pl.DataFrame,
                                columns: Iterable[xi_types.Column]) -> None:
        """ Write the value of the given columns of the given data-frame to the data store. """
        if not self._fetch_individual_series:
            #
            #
            #
            raise RuntimeError("Frames may only be stored as one series per table.")

        #
        for c in columns:
            #
            column_df = value.lazy().select(list(entity.unique_index_names) + [c.name])

            #
            col_renames = {index_label: self._encode_column_name(index_label)
                           for index_label in entity.unique_index_names}
            col_renames[c.name] = self._encode_column_name(c.entity_name)
            column_df = column_df.rename(col_renames)

            dtypes = {
                self._encode_column_name(index_label): self._get_polars_export_type(ind.dtype)
                for (index_label, ind) in zip(entity.unique_index_names, entity.index)
            }
            dtypes[self._encode_column_name(c.entity_name)] = self._get_polars_export_type(c.dtype)
            table_name = self._encode_entity_table_name(c)

            self._export_polars_table(column_df, table_name, dtypes=dtypes)

    def save_entities(self, entity_filter: Callable[[xi_types.Entity], bool]) -> None:
        """ Write the given entities of the given container to the data store. """
        #
        exceptions: List[BaseException] = []

        with self._connect():
            #
            scalar_values: SingleValueDict = {dtype: {} for dtype in xi_types.ALL_BASIC_TYPE}
            parameter_values: SingleValueDict = {dtype: {} for dtype in xi_types.ALL_BASIC_TYPE}

            for entity in TableConnector._get_entities(self._data_container, entity_filter):
                with self._slow_tasks_monitor.task(f'Saving data from entity {entity.name}'):
                    try:
                        if entity.name not in self._data_container.__dict__:
                            raise KeyError(f"Entity {entity.name} declared but not initialized.")

                        #
                        entity_value = self._data_container.__dict__[entity.name]
                        with self._slow_tasks_monitor.task(f'Validating data in entity {entity.name}'):
                            if isinstance(entity, xi_types.DataFrameBase):
                                columns = [col for col in entity.columns if entity_filter(col)]
                                entity.check_value(entity_value, columns=columns,
                                                   allow_duplicate_indices=self._allow_duplicate_indices)
                            else:
                                entity.check_value(entity_value, allow_duplicate_indices=self._allow_duplicate_indices)

                        #
                        if isinstance(entity, xi_types.Param):
                            parameter_values[entity.dtype][entity.name] = entity_value
                        elif isinstance(entity, xi_types.Scalar):
                            scalar_values[entity.dtype][entity.name] = entity_value
                        elif isinstance(entity, xi_types.Index):
                            self._save_index(entity, entity_value)
                        elif isinstance(entity, xi_types.PolarsIndex):
                            self._save_polars_index(entity, entity_value)
                        elif isinstance(entity, xi_types.Series):
                            self._save_series(entity, entity_value)
                        elif isinstance(entity, xi_types.DataFrame):
                            self._save_data_frame(entity, entity_value, columns)
                        elif isinstance(entity, xi_types.PolarsDataFrame):
                            self._save_polars_data_frame(entity, entity_value, columns)
                        else:
                            raise UnexpectedEntityTypeError(entity)

                    except BaseException as e:  # pylint: disable=broad-except
                        #
                        #
                        print(f"ERROR: Failed to save entity {entity.name} for reason: {e.__class__}: {e}",
                              file=sys.stderr)
                        exceptions.append(e)

            #
            try:
                with self._slow_tasks_monitor.task(f'Saving data from parameter entities'):
                    self._save_scalars(parameter_values, 'PARAM')
            except BaseException as e:  # pylint: disable=broad-except
                #
                #
                print(f"ERROR: Failed to save parameters for reason: {e.__class__}: {e}", file=sys.stderr)
                exceptions.append(e)

            try:
                with self._slow_tasks_monitor.task(f'Saving data from scalar entities'):
                    self._save_scalars(scalar_values, 'SCALAR')
            except BaseException as e:  # pylint: disable=broad-except
                #
                #
                print(f"ERROR: Failed to save scalars for reason: {e.__class__}: {e}", file=sys.stderr)
                exceptions.append(e)

        #
        if exceptions:
            raise exceptions[0]

    @abstractmethod
    @contextmanager
    def _connect(self):
        raise RuntimeError(ERR_ABSTRACT)
