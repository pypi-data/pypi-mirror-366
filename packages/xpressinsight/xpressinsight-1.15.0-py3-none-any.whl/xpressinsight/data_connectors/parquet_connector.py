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

import os
from typing import Dict, Optional, Union, Type
from contextlib import contextmanager
import datetime
import sys
from packaging import version

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ..entities import basic_types as xi_types
from .. import polars_shims as pl
from ..polars_shims import selectors as cs
from ..slow_tasks_monitor import SlowTasksMonitor
from .table_connector import TableConnector
from .data_connector import SingleValueDict

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override


PARQUET_DIR = "parquet"

EXPORT_TYPE_MAP: Dict[Type[xi_types.BasicType], pa.DataType] = {
    xi_types.boolean: pa.bool_(),
    xi_types.integer: pa.int32(),
    xi_types.string: pa.utf8(),
    xi_types.real: pa.float64(),
}

POLARS_EXPORT_TYPE_MAP: Dict[Type[xi_types.BasicType], pl.DataType] = {
    xi_types.boolean: pl.Boolean(),
    xi_types.integer: pl.Int32(),
    xi_types.string: pl.Utf8(),
    xi_types.real: pl.Float64
} if pl.polars_available else {}


class ParquetConnector(TableConnector):
    """TableConnector implementation that reads/writes Parquet files. Further subclasses will add behaviours specific
     to interactions with Mosel/mmarrow or with Insight Worker."""
    def __init__(self, data_container, parquet_dir: str,
                 fetch_individual_series: bool = True,
                 slow_tasks_monitor: Optional[SlowTasksMonitor] = None,
                 allow_duplicate_indices: Optional[bool] = None,
                 single_parameters_table: bool = False):
        super().__init__(data_container, fetch_individual_series=fetch_individual_series,
                         slow_tasks_monitor=slow_tasks_monitor,
                         allow_duplicate_indices=allow_duplicate_indices,
                         single_parameters_table=single_parameters_table)
        self._parquet_dir = parquet_dir

    def _get_export_type(self, src_type: Type[xi_types.BasicType]) -> pa.DataType:
        return EXPORT_TYPE_MAP[src_type]

    def _get_polars_export_type(self, src_type: Type[xi_types.BasicType]) -> pl.DataType:
        return POLARS_EXPORT_TYPE_MAP[src_type]

    def _encode_column_name(self, ident: str) -> str:
        return ident

    def _decode_column_name(self, ident: str) -> str:
        return ident

    def clean(self):
        """ Creates directory structure for parquet data repository if it does not exist.
        If parquet folder contains parquet files, delete all of them. """
        #
        #
        try:
            os.makedirs(self._parquet_dir, exist_ok=True)
            files = os.listdir(self._parquet_dir)

            for file in files:
                if file.endswith(".parquet"):
                    os.remove(os.path.join(self._parquet_dir, file))
        except OSError as err:
            raise OSError(f'Could not clean data repository directory: "{self._parquet_dir}".\nOSError: {err}') from err

    def _does_db_exist(self) -> bool:
        """Returns True iff data repository directory exists"""
        return os.path.isdir(self._parquet_dir)

    def _check_db_exists(self):
        """Checks if the SQLite database files exists, if it does not, raises and exception"""

        if not self._does_db_exist():
            raise FileNotFoundError(f'Cannot find data repository directory: "{self._parquet_dir}".')

    def is_empty(self) -> bool:
        return not self._does_db_exist()

    def _save_single_values_db(self, prefix: str, values: SingleValueDict, merge : bool = False):
        """Saves SingleValueDict to the database"""

        assert prefix in ("SCALAR", "PARAM", "META")

        if merge:
            values = TableConnector._merge_single_value_dicts(self._load_single_values_db(prefix), values)

        for dtype in xi_types.ALL_BASIC_TYPE:
            #
            if dtype in values and values[dtype]:
                #
                #
                #
                #
                table_name = f"{prefix}_{dtype.__name__}"
                schema = pa.schema([
                    pa.field('Name', pa.utf8(), False),
                    pa.field('Value', EXPORT_TYPE_MAP[dtype], False)
                ])
                # noinspection PyArgumentList
                arrow_table = pa.Table.from_pydict({
                    'Name': values[dtype].keys(),
                    'Value': values[dtype].values()
                }, schema=schema)
                self._export_table(arrow_table, table_name, dtype={})
                del arrow_table

    def _get_pq_file_name(self, table_name):
        return table_name + '.parquet'

    def _get_pq_file_path(self, table_name):
        return os.path.join(self._parquet_dir, self._get_pq_file_name(table_name))

    def _has_table(self, table_name: str) -> bool:
        return os.path.isfile(self._get_pq_file_path(table_name))

    @staticmethod
    def _int64_conversion(table: pd.DataFrame, schema: pa.Schema):
        for field in schema:
            if pa.types.is_integer(field.type) and table[field.name].dtype != np.int64:
                table[field.name] = table[field.name].astype(np.int64, copy=False)

    @staticmethod
    def _int64_conversion_polars(table: pl.LazyFrame) -> pl.LazyFrame:
        return table.cast({cs.integer(): pl.Int64})

    @override
    def _import_table(self, table_name: str) -> pd.DataFrame:
        """Import parquet file as flat DataFrame with indices as normal columns. """
        #
        start_time = datetime.datetime.now(datetime.timezone.utc)

        #
        #
        arrow_table = pq.read_table(self._get_pq_file_path(table_name))
        #
        table = arrow_table.to_pandas(ignore_metadata=True)

        #
        #
        ParquetConnector._int64_conversion(table, arrow_table.schema)
        del arrow_table

        if self._verbose:
            end_time = datetime.datetime.now(datetime.timezone.utc)
            print(f'Imported {table_name}: {end_time - start_time}')

        return table

    @staticmethod
    def _get_schema(df: pd.DataFrame, dtype: Dict[str, pa.DataType], data_col_nullable: bool):
        #
        return pa.schema(
            #
            #
            [pa.field(f_name, f_type, f_name not in df.index.names and data_col_nullable)
             for f_name, f_type in dtype.items()]
        )

    def _export_table(self, df: Union[pa.Table, pd.DataFrame, pd.Series], table_name: str,
                      dtype: Dict[str, pa.DataType], index: bool = True, data_col_nullable: bool = False):
        start_time = datetime.datetime.now(datetime.timezone.utc)

        #
        if isinstance(df, pd.Series):
            #
            df = df.to_frame()

        if isinstance(df, pd.DataFrame):
            #
            schema = self._get_schema(df, dtype, data_col_nullable)
            #
            #
            if df.size == 0:
                arrow_table = pa.table(schema=schema, data={name: [] for (name, value) in dtype.items()})
            else:
                # noinspection PyArgumentList
                arrow_table = pa.Table.from_pandas(df, schema=schema, preserve_index=index)
        elif isinstance(df, pa.Table):
            #
            arrow_table = df
        else:
            raise TypeError(f'Unexpected type "{type(df)}" for table "{table_name}".')

        #
        #
        pq.write_table(arrow_table, where=self._get_pq_file_path(table_name), compression='NONE')
        del arrow_table

        if self._verbose:
            end_time = datetime.datetime.now(datetime.timezone.utc)
            print(f'Exported {table_name}: {end_time - start_time}')

    def _import_polars_table(self, table_name: str) -> pl.LazyFrame:
        """ Import named table to a Polars DataFrame. """
        start_time = datetime.datetime.now(datetime.timezone.utc)

        #
        df = pl.scan_parquet(self._get_pq_file_path(table_name))

        #
        #
        df = ParquetConnector._int64_conversion_polars(df)

        if self._verbose:
            end_time = datetime.datetime.now(datetime.timezone.utc)
            print(f'Imported {table_name}: {end_time - start_time}')

        return df

    def _export_polars_table(self, df: Union[pl.DataFrame, pl.LazyFrame], table_name: str,
                             dtypes: Dict[str, pl.DataType]) -> None:
        """ Export Polars data-frame to named table. """
        start_time = datetime.datetime.now(datetime.timezone.utc)

        #
        df = df.cast(dtypes)

        #
        #
        #
        #
        if isinstance(df, pl.LazyFrame):
            df = df.collect()

        df.write_parquet(file=self._get_pq_file_path(table_name), compression='uncompressed')

        if self._verbose:
            end_time = datetime.datetime.now(datetime.timezone.utc)
            print(f'Exported {table_name}: {end_time - start_time}')

    @contextmanager
    def _connect(self):
        """ Check if parquet directory exists. """
        self._check_db_exists()
        try:
            yield self._parquet_dir
        finally:
            pass


class MoselParquetConnector(ParquetConnector):
    """ Variant of the ParquetConnector that reads/writes Parquet files written by Mosel. """

    def __init__(self, app, parquet_dir: Optional[str] = None):
        super().__init__(app,
                         parquet_dir=os.path.join(app.insight.work_dir, PARQUET_DIR)
                                     if parquet_dir is None else parquet_dir,
                         fetch_individual_series=True,
                         slow_tasks_monitor=app._slow_tasks_monitor,
                         allow_duplicate_indices=app.app_cfg.allow_duplicate_indices)
