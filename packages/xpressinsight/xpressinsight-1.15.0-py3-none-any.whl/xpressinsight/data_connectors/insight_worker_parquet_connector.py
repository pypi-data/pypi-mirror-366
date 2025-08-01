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

import os
from typing import Dict, Optional, Type, Union, List, Callable

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from ..entities import basic_types as xi_types
from ..slow_tasks_monitor import SlowTasksMonitor
from .. import entities as xi_entities
from .parquet_connector import ParquetConnector


#
INSIGHT_WORKER_VALUE_TYPES_FOR_BASIC_TYPES: Dict[Optional[Type[xi_types.BasicType]], Optional[str]] = {
    xi_types.integer: 'INTEGER',
    xi_types.real: 'REAL',
    xi_types.string: 'STRING',
    xi_types.boolean: 'BOOLEAN',
    None: None
}


class ArraysTableColumn(BaseModel):
    """ Python implementation of Insight DTO class
        com.fico.xpress.insight.shared.parquet.converter.ArraysTableDescription.Array """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    entity_name: str
    column_name: Optional[str]
    value_type: Optional[str]
    empty_value: Optional[Union[int, float, str, bool]]
    use_default_empty_value: Optional[bool] = None


class ArraysTableIndex(BaseModel):
    """ Python implementation of Insight DTO class
        com.fico.xpress.insight.shared.parquet.converter.ArraysTableDescription.Index """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    column_name: Optional[str]
    value_type: Optional[str]


class ArraysTableDescription(BaseModel):
    """ Python implementation of Insight DTO class
        com.fico.xpress.insight.shared.parquet.converter.ArraysTableDescription """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    arrays: List[ArraysTableColumn]
    indexes: Optional[List[ArraysTableIndex]]
    type: str = "ARRAYS"


class ScalarsTableEntry(BaseModel):
    """ Python implementation of Insight DTO class
        com.fico.xpress.insight.shared.parquet.converter.ScalarsTableDescription.Scalar """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    entity_name: str
    value_type: Optional[str]
    skip_on_type_mismatch: bool = False


class ScalarsTableDescription(BaseModel):
    """ Python implementation of Insight DTO class
        com.fico.xpress.insight.shared.parquet.converter.ScalarsTableDescription """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    scalars: List[ScalarsTableEntry]
    type: str = "SCALARS"


class SetTableDescription(BaseModel):
    """ Python implementation of Insight DTO class
        com.fico.xpress.insight.shared.parquet.converter.SetTableDescription """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    entity_name: str
    column_name: Optional[str]
    value_type: Optional[str]
    type: str = "SET"


class ConversionDescription(BaseModel):
    """ Python implementation of Insight DTO class
        com.fico.xpress.insight.shared.parquet.converter.ConversionDescription """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    tables: Dict[str, Union[ScalarsTableDescription, SetTableDescription, ArraysTableDescription]]


class InsightWorkerParquetConnector(ParquetConnector):
    """ Variant of the ParquetConnector that reads scenario data for the given scenario directly from the
        Insight worker. """
    def __init__(self, app, data_container, scenario_path_or_id: str, parquet_dir: str, fetch_individual_series: bool,
                 input_only: bool, slow_tasks_monitor: Optional[SlowTasksMonitor] = None):
        super().__init__(data_container, parquet_dir=parquet_dir, fetch_individual_series=fetch_individual_series,
                         single_parameters_table=True, slow_tasks_monitor=slow_tasks_monitor)
        self._app = app
        self._scenario_path_or_id = scenario_path_or_id
        self._input_only = input_only

    def _make_conversion_description(self, entity_filter: Callable[[xi_entities.Entity], bool]
                                     ) -> ConversionDescription:
        """ Creates a conversion description to describe to the Insight worker which entities need to be written into
            which Parquet files """
        #
        scalar_entries_by_type: Dict[Type[xi_types.BASIC_TYPE], List[ScalarsTableEntry]] = {
            dtype: [] for dtype in xi_types.ALL_BASIC_TYPE
        }
        #
        tables: Dict[str, Union[ScalarsTableDescription, SetTableDescription, ArraysTableDescription]] = {}

        for entity in ParquetConnector._get_entities(self._data_container, entity_filter):
            if isinstance(entity, xi_entities.Param):
                if 'PARAM' not in tables:
                    string_type = INSIGHT_WORKER_VALUE_TYPES_FOR_BASIC_TYPES[xi_types.string]
                    tables['PARAM'] = ArraysTableDescription(
                        arrays=[ArraysTableColumn(entity_name='parameters', column_name='Value',
                                                  value_type=string_type,
                                                  empty_value='')],
                        indexes=[ArraysTableIndex(column_name='Name', value_type=string_type)]
                    )

            elif isinstance(entity, xi_entities.Scalar):
                if entity.dtype:
                    scalar_entries_by_type[entity.dtype].append(ScalarsTableEntry(
                        entity_name=entity.entity_name,
                        value_type=INSIGHT_WORKER_VALUE_TYPES_FOR_BASIC_TYPES[entity.dtype]
                    ))

                else:
                    #
                    for dtype in xi_types.ALL_BASIC_TYPE:
                        scalar_entries_by_type[dtype].append(ScalarsTableEntry(
                            entity_name=entity.entity_name,
                            value_type=INSIGHT_WORKER_VALUE_TYPES_FOR_BASIC_TYPES[dtype],
                            skip_on_type_mismatch=True
                        ))

            elif isinstance(entity, xi_entities.IndexBase):
                tables[self._encode_entity_table_name(entity)] = SetTableDescription(
                    entity_name=entity.entity_name,
                    column_name=entity.name,
                    value_type=INSIGHT_WORKER_VALUE_TYPES_FOR_BASIC_TYPES[entity.dtype])

            elif isinstance(entity, xi_entities.Indexed):
                #
                index_column_names = entity.index_names
                index_types = entity.index_types
                has_some_index_info = bool(index_column_names) or bool(index_types)
                if has_some_index_info:
                    num_indexes = len(index_column_names) if index_column_names else len(index_types)

                    if not index_column_names:
                        index_column_names = [None for _ in range(0, num_indexes)]
                    if not index_types:
                        index_types = [None for _ in range(0, num_indexes)]
                    if len(index_types) != len(index_column_names):
                        raise RuntimeError(f'Same numbers of index names and types must be given for entity '
                                           f'"{entity.name}".')

                indexes = [
                    ArraysTableIndex(
                        column_name=name,
                        value_type=INSIGHT_WORKER_VALUE_TYPES_FOR_BASIC_TYPES[dtype]
                    ) for (name, dtype) in zip(index_column_names, index_types)
                ] if has_some_index_info else None

                if isinstance(entity, xi_entities.Series):
                    tables[self._encode_entity_table_name(entity)] = ArraysTableDescription(
                        arrays=[ArraysTableColumn(
                            entity_name=entity.entity_name,
                            column_name=entity.series_name,
                            value_type=INSIGHT_WORKER_VALUE_TYPES_FOR_BASIC_TYPES[entity.dtype],
                            #
                            empty_value=None,
                            use_default_empty_value=False)],
                        indexes=indexes
                    )

                else:
                    assert isinstance(entity, xi_entities.DataFrameBase)
                    if self._fetch_individual_series:
                        for col in entity.columns:
                            if entity_filter(col):
                                tables[self._encode_entity_table_name(col)] = ArraysTableDescription(
                                    arrays=[ArraysTableColumn(
                                        entity_name=col.entity_name,
                                        column_name=self._encode_column_name(col.entity_name),
                                        value_type=INSIGHT_WORKER_VALUE_TYPES_FOR_BASIC_TYPES[col.dtype],
                                        #
                                        empty_value=None,
                                        use_default_empty_value=False)],
                                    indexes=indexes
                                )

                    else:
                        tables[self._encode_entity_table_name(entity)] = ArraysTableDescription(
                            arrays=[
                                ArraysTableColumn(
                                    entity_name=col.entity_name,
                                    column_name=col.name,
                                    value_type=INSIGHT_WORKER_VALUE_TYPES_FOR_BASIC_TYPES[col.dtype],
                                    empty_value=col.default,
                                    #
                                    #
                                    use_default_empty_value=(col.default is None and
                                                             isinstance(entity, xi_entities.DataFrame))
                                ) for col in entity.columns if entity_filter(col)],
                            indexes=indexes
                        )

            else:
                raise RuntimeError(f'Entity "{entity.name}" has unrecognized type "{type(entity)}"')

        #
        for (dtype, scalar_entries) in scalar_entries_by_type.items():
            if scalar_entries:
                tables[f"SCALAR_{dtype.__name__}"] = ScalarsTableDescription(scalars=scalar_entries)

        return ConversionDescription(tables={
            self._get_pq_file_name(table_name): table
            for (table_name, table) in tables.items()
        })

    def load_entities(self, entity_filter: Callable[[xi_entities.Entity], bool]):
        #
        conversion_description = self._make_conversion_description(entity_filter)

        #
        conversion_description_file = os.path.join(self._parquet_dir, 'tables.json')
        # pylint does not support the dataclasses_json decorator, so reports the to_json() function does not
        #
        # pylint: disable=no-member
        conversion_description_json = conversion_description.model_dump_json(by_alias=True)
        with open(conversion_description_file, 'w', encoding="utf-8") as file:
            file.write(conversion_description_json)

        #
        self._app.insight._fetch_scenario_data_parquet(scenario_path_or_id=self._scenario_path_or_id,
                                                       output_dir=self._parquet_dir,
                                                       conversion_description_file=conversion_description_file,
                                                       input_only=self._input_only)

        #
        try:
            super().load_entities(entity_filter)
        except Exception as e:
            #
            print(f"ERROR: Failed to restore entity data fetched from the Insight worker for reason '{e}'; "
                  f"the following description of the data fetched may be useful to Xpress "
                  f"Insight support in diagnosing this issue: {conversion_description_json}")
            raise e

    def save_entities(self, entity_filter: Callable[[xi_entities.Entity], bool]):
        raise RuntimeError("Saving entities directly to the Insight worker is not supported at this time.")
