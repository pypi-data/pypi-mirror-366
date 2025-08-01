"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from collections import Counter
from contextlib import contextmanager
from enum import Enum
from typing import Dict, Sequence, Union, Type, List, Optional, Tuple, TypeVar
import sys

import pandas as pd
import pyarrow as pa

from .. import entities as xi_types
from .. import polars_shims as pl
from ..entities.basic_types import PANDAS_DTYPE_TYPES_FOR_INSIGHT_TYPES, BASIC_TYPE, BASIC_PANDAS_DTYPE_MAP, \
    BASIC_POLARS_DTYPE_MAP
from ..entities.index import get_index_level_names
from ..entities_config import EntitiesContainer
from ..slow_tasks_monitor import SlowTasksMonitor
from .table_connector import TableConnector, TABLE_PREFIX_ENTITY
from ..scenario.models import EntityData, ScenarioData, ModelSchema, ModelEntity

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override


ERR_READ_ONLY = "Data-connector is read-only"

IMPORTED_TABLE = TypeVar('IMPORTED_TABLE', bound=Union[pd.DataFrame, pl.LazyFrame])


class StructType(Enum):
    """ Enumeration of possible structural types of Insight entities. """
    SCALAR = 1
    SET = 2
    ARRAY = 3


DATA_TYPE_TO_STRUCT_TYPE = {
    'BOOLEAN': StructType.SCALAR,
    'INTEGER': StructType.SCALAR,
    'REAL': StructType.SCALAR,
    'STRING': StructType.SCALAR,
    'DECISION_VARIABLE': StructType.SCALAR,
    'CONSTRAINT': StructType.SCALAR,
    'MODEL': StructType.SCALAR,
    'CONSTRAINT_TYPE': StructType.SCALAR,
    'VARIABLE_TYPE': StructType.SCALAR,
    'PROBLEM_STATUS': StructType.SCALAR,
    'SET': StructType.SET,
    'ARRAY': StructType.ARRAY,
}

VALUE_TYPE_TO_BASIC_TYPE = {
    'BOOLEAN': xi_types.boolean,
    'INTEGER': xi_types.integer,
    'REAL': xi_types.real,
    'STRING': xi_types.string,
    'DECISION_VARIABLE': xi_types.real,
    'CONSTRAINT': xi_types.real,
    'MODEL': xi_types.real,
    'CONSTRAINT_TYPE': xi_types.string,
    'VARIABLE_TYPE': xi_types.string,
    'PROBLEM_STATUS': xi_types.string,
}


class RestApiEntity:
    """
    Simple representation of an entity's type.
    """
    name: str
    struct_type: StructType
    element_type: BASIC_TYPE
    index_names: Optional[List[str]]

    def __init__(self, entity: ModelEntity):
        self.name = entity.name
        self.struct_type = DATA_TYPE_TO_STRUCT_TYPE[entity.data_type]
        if self.struct_type == StructType.SCALAR:
            self.element_type = VALUE_TYPE_TO_BASIC_TYPE[entity.data_type]
        else:
            self.element_type = VALUE_TYPE_TO_BASIC_TYPE[entity.element_type]
        self.index_names = entity.index_sets


class RestApiConnector(TableConnector):
    """
    Read-only implementation of TableConnector that populates from the objects output by calls to the Insight REST
    API. Note does not call through to the REST API itself, only reads from model structures passed in.
    """
    _source: Dict[str, EntityData]
    _schema: Dict[str, RestApiEntity]

    def __init__(self, data_container: EntitiesContainer, source: ScenarioData, source_schema: ModelSchema,
                 slow_tasks_monitor: Optional[SlowTasksMonitor] = None):
        super().__init__(data_container, fetch_individual_series=True, single_parameters_table=True,
                         slow_tasks_monitor=slow_tasks_monitor)
        self._schema = {entity.name: RestApiEntity(entity) for entity in source_schema.entities.values()}
        self._source = {data.entity_name: data for data in source.entities.values()}
        if len(self._source) != len(source.entities):
            raise ValueError('Received multiple values for the following entities: ' +
                             str([name for (name, count) in
                                  Counter(data.entity_name for data in source.entities.values()).items()
                                  if count > 0]))

    @override
    def _get_export_type(self, src_type: Type[xi_types.BasicType]) -> pa.DataType:
        raise RuntimeError(ERR_READ_ONLY)

    @override
    def _get_polars_export_type(self, src_type: Type[xi_types.BasicType]) -> pl.DataType:
        raise RuntimeError(ERR_READ_ONLY)

    @override
    def _encode_entity_table_name(self, entity: xi_types.EntityBase) -> str:
        #
        #
        if isinstance(entity, xi_types.Column):
            return self._encode_table_name(f'{entity._data_frame.name}.{entity.name}')

        return self._encode_table_name(entity.name)

    def _find_entity_from_table_name(self, table_name: str) -> xi_types.Entity:
        """ Given an encoded entity table name as returned by _encode_entity_table_name, find the corresponding
            Entity. """
        if not table_name.startswith(TABLE_PREFIX_ENTITY):
            raise ValueError(f'Table name "{table_name}" was not an entity table')
        entity_name = table_name[len(TABLE_PREFIX_ENTITY):]
        entity = self._data_container.entities_cfg.get_entity(entity_name)
        if entity is None:
            raise KeyError(f'Entity "{table_name}" not found')
        if not isinstance(entity, xi_types.Entity):
            raise TypeError(f'Expected non-composed entity for "{table_name}" but found "{type(entity)}"')
        return entity

    @override
    def _encode_table_name(self, name: str) -> str:
        #
        return TABLE_PREFIX_ENTITY + name

    @override
    def _decode_table_name(self, name: str) -> str:
        if not name.startswith(TABLE_PREFIX_ENTITY):
            raise ValueError(f'"{name} is not an entity table')

        return name[len(TABLE_PREFIX_ENTITY):]

    @override
    def _encode_column_name(self, ident: str) -> str:
        return ident

    @override
    def _decode_column_name(self, ident: str) -> str:
        return ident

    @override
    def _does_db_exist(self) -> bool:
        return True

    @override
    def _check_db_exists(self) -> None:
        pass

    @override
    def clean(self) -> None:
        raise RuntimeError(ERR_READ_ONLY)

    def is_empty(self) -> bool:
        return len(self._source) > 0

    @override
    def _has_table(self, table_name: str) -> bool:
        if table_name.startswith(TABLE_PREFIX_ENTITY):
            entity = self._find_entity_from_table_name(table_name)
            return entity.name in self._source

        if table_name.startswith('SCALAR_'):
            return True

        return False

    def _import_pandas_or_polars_table(self, table_name: str, table_type: Type[IMPORTED_TABLE]) -> IMPORTED_TABLE:
        """ Import as either Pandas or Polars table, depending upon table_type parameter. """
        #
        #
        if table_type == pd.DataFrame:
            column_types_map = BASIC_PANDAS_DTYPE_MAP
            import_list_func = RestApiConnector._import_list_as_pandas_table
            import_dict_func = RestApiConnector._import_dict_as_pandas_table
        elif table_type == pl.LazyFrame:
            column_types_map = BASIC_POLARS_DTYPE_MAP
            import_list_func = RestApiConnector._import_list_as_polars_table
            import_dict_func = RestApiConnector._import_dict_as_polars_table
        else:
            raise KeyError(f'Unrecognized table type "{table_type}"')

        #
        entity = self._find_entity_from_table_name(table_name)
        if entity.entity_name not in self._source:
            raise KeyError(f'Table "{entity.entity_name}" not found in data-connector')
        entity_data = self._source[entity.entity_name]

        #
        #
        schema_entity = self._schema[entity.entity_name]

        #
        if schema_entity.struct_type == StructType.SET:
            #
            if not isinstance(entity, xi_types.IndexBase):
                raise TypeError(f'Set-type entity "{entity.entity_name}" must be loaded into an Index or PolarsIndex, '
                                f'but found "{type(entity)}"')
            if entity_data.values is None:
                raise TypeError(f'No values returned for entity "{entity.entity_name}"')
            return import_list_func(entity_data.values, entity.name, column_types_map[schema_entity.element_type])

        if schema_entity.struct_type == StructType.ARRAY:
            if not isinstance(entity, (xi_types.Series, xi_types.Column)):
                raise TypeError(f'Array-type entity "{entity.entity_name}" must be loaded into a Series, DataFrame '
                                f'or PolarsDataFrame, but found "{type(entity)}"')
            if entity_data.array is None:
                raise TypeError(f'No values returned for entity "{entity.entity_name}"')

            #
            if entity.index_names and len(entity.index_names) != len(schema_entity.index_names):
                raise TypeError(f'Array-type entity "{entity.entity_name}" has {len(schema_entity.index_names)} '
                                f'indexes but Python entity definition requires {len(entity.index_names)}')
            if entity.index_types and len(entity.index_types) != len(schema_entity.index_names):
                raise TypeError(f'Array-type entity "{entity.entity_name}" has {len(schema_entity.index_names)} '
                                f'indexes but Python entity definition requires {len(entity.index_types)}')

            index_names = entity.unique_index_names or get_index_level_names(schema_entity.index_names)
            index_types = [column_types_map[self._schema[name].element_type] for name in schema_entity.index_names]
            index_columns = list(zip(index_names, index_types))
            value_column = [(
                entity.series_name if isinstance(entity, xi_types.Series) else entity.entity_name,
                column_types_map[schema_entity.element_type
            ])]
            return import_dict_func(entity_data.array, index_columns + value_column)

        raise TypeError(f"Unsupported entity type {schema_entity.struct_type}")

    @override
    def _import_table(self, table_name: str) -> pd.DataFrame:
        if table_name.startswith('SCALAR_'):
            return self._import_scalars_table(table_name)
        if table_name == 'PARAM':
            return self._import_parameters_table()
        return self._import_pandas_or_polars_table(table_name, pd.DataFrame)

    @override
    def _import_polars_table(self, table_name: str) -> pl.LazyFrame:
        #
        return self._import_pandas_or_polars_table(table_name, pl.LazyFrame)

    def _import_scalars_table(self, table_name: str) -> pd.DataFrame:
        """ Import the scalars table for the given type. """
        assert table_name.startswith('SCALAR_')
        requested_type = xi_types.__dict__[table_name[len('SCALAR_'):]]
        scalars_dict = {entity_data.entity_name: entity_data.value for entity_data in self._source.values()
                        if (self._schema[entity_data.entity_name].struct_type == StructType.SCALAR and
                            self._schema[entity_data.entity_name].element_type == requested_type)}
        #
        return pd.DataFrame({'Name': pd.Series(list(scalars_dict.keys()), dtype=str),
                             'Value': pd.Series(list(scalars_dict.values()),
                                                dtype=BASIC_PANDAS_DTYPE_MAP[requested_type])})

    def _import_parameters_table(self) -> pd.DataFrame:
        """ Import the parameters table. """
        params_dict = self._source['parameters'].array
        #
        return pd.DataFrame({'Name': pd.Series(list(params_dict.keys()), dtype=str),
                             'Value': pd.Series(list(params_dict.values()), dtype=str)})

    @staticmethod
    def _import_list_as_pandas_table(data: List, column_name: str, column_dtype: PANDAS_DTYPE_TYPES_FOR_INSIGHT_TYPES
                                     ) -> pd.DataFrame:
        """ Transform a Python List to a Pandas DataFrame. """
        return pd.DataFrame(data=data, columns=[column_name], dtype=column_dtype)

    @staticmethod
    def _import_dict_as_pandas_table(data: Dict,
                                     columns: Sequence[Tuple[str, PANDAS_DTYPE_TYPES_FOR_INSIGHT_TYPES]]
                                     ) -> pd.DataFrame:
        """ Transform a (possibly nested) dictionary into a Python DataFrame. """
        #
        if len(columns) == 2:
            #
            return RestApiConnector._import_unnested_dict_as_pandas_table(data, columns)

        #
        if len(data) == 0:
            #
            return pd.DataFrame({name: pd.Series(name=name, dtype=dtype) for (name, dtype) in columns})

        #
        table_parts = []
        (col_name, col_dtype) = columns[0]
        for (key, value) in data.items():
            #
            table_part = RestApiConnector._import_dict_as_pandas_table(value, columns[1:])

            #
            table_part.insert(0, col_name, key)
            if col_dtype is not None:
                table_part = table_part.astype({col_name: col_dtype}, copy=False)

            #
            table_parts.append(table_part)

        return pd.concat(table_parts, ignore_index=True)

    @staticmethod
    def _import_unnested_dict_as_pandas_table(data: Dict,
                                              columns: Sequence[Tuple[str, PANDAS_DTYPE_TYPES_FOR_INSIGHT_TYPES]] = None
                                              ) -> pd.DataFrame:
        """ Transform an un-nested dictionary into a Python data-frame. """
        #
        df = pd.DataFrame.from_records(data=list(data.items()), columns=[name for (name, dtype) in columns])

        #
        types_mapping = {name: dtype for (name, dtype) in columns}
        df = df.astype(types_mapping, copy=False)

        return df

    @override
    def _export_table(self, df: Union[pd.DataFrame, pd.Series], table_name: str, dtype: Dict[str, pa.DataType],
                      index: bool = True, data_col_nullable: bool = False) -> None:
        raise RuntimeError(ERR_READ_ONLY)

    @staticmethod
    def _import_list_as_polars_table(data: List, column_name: str, column_dtype: pl.DataType) -> pl.LazyFrame:
        """ Transform a Python List to a Polars LazyFrame. """
        return pl.LazyFrame(data=data, schema={column_name: column_dtype})

    @staticmethod
    def _import_dict_as_polars_table(data: Dict, columns: Sequence[Tuple[str, pl.DataType]]) -> pl.LazyFrame:
        """ Transform a (possibly nested) dictionary into a Polars LazyFrame. """
        #
        if len(data) == 0:
            return pl.LazyFrame(schema=dict(columns))

        #
        if len(columns) == 2:
            #
            return RestApiConnector._import_unnested_dict_as_polars_table(data, columns=columns)

        #
        (column_name, column_dtype) = columns[0]
        table_parts = []
        for (key, value) in data.items():
            #
            table_part = RestApiConnector._import_dict_as_polars_table(value, columns=columns[1:])
            #
            table_part = table_part.select([
                pl.lit(key, dtype=column_dtype).alias(column_name),
                pl.selectors.all()
            ])
            table_parts.append(table_part)

        return pl.concat(table_parts)

    @staticmethod
    def _import_unnested_dict_as_polars_table(data: Dict, columns: Sequence[Tuple[str, pl.DataType]]) -> pl.LazyFrame:
        """ Transform an un-nested dictionary into a Python data-frame with columns 'idx' and table_name. """
        [index_name, value_name] = [name for (name, dtype) in columns]
        return pl.LazyFrame(
            data={index_name: data.keys(), value_name: data.values()},
            schema=dict(columns)
        )

    @override
    def _export_polars_table(self, df: Union[pl.DataFrame, pl.LazyFrame], table_name: str,
                             dtypes: Dict[str, pl.DataType]) -> None:
        raise RuntimeError(ERR_READ_ONLY)

    @override
    @contextmanager
    def _connect(self):
        yield 'nothing'
