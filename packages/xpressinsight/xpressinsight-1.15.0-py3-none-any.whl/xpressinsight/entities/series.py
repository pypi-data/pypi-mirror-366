"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Define the Series entity type.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2025 Fair Isaac Corporation. All rights reserved.
"""

from typing import Optional, Union, List, Mapping, Any, Iterable
import sys

import pandas as pd

from .basic_types import BASIC_TYPE, check_type_np
from .entity import Entity, Hidden, Manage, EntityBase
from .index import IndexedPandas

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override


class Series(Entity, IndexedPandas):
    """
    The configuration of a *Series* entity, a declaration of a pandas `Series` data structure. Use the helper function
    `xpressinsight.types.Series` to declare a Series entity in an app, rather than instantiating
    `xpressinsight.Series` directly.

    Notes
    -----
    In older versions of `xpressinsight`, it was possible to use the `Series` as the annotation for an entity.
    This syntax is now deprecated and should not be used in new apps; it will not be supported in Python 3.12 and
    above.

    See Also
    --------
    types.Series
    """

    __series_name: Optional[str]

    #
    #
    # noinspection PyShadowingBuiltins
    # pylint: disable-next=too-many-arguments
    def __init__(
            self,
            index: Optional[Union[str, List[str]]] = None,
            dtype: BASIC_TYPE = None,
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
            entity_name: str = None,
            series_name: str = None,
            index_types: List[BASIC_TYPE] = None
            #
    ):
        """
        Initializes `Series`.

        Parameters
        ----------
        index : Optional[Union[str, List[str]]], optional
            The name of the index to use, or list of names for multiple indices. Each entry must be the name
            of an `Index` or `PolarsIndex` type entity within the app.
            When used in an `AppConfig`-decorated class, this is required and the same index may appear in the
            list multiple times.
            When used in a `ScenarioData`-decorated class, this is optional if given, the names must be unique and
            there must be one for each index column. If not specified, names derived from the index entities in the
            source scenario will be used.
        index : Union[str, List[str]], optional
            The name of the index to use, or list of names for multiple indices. Where entity is used in an app
            definition, the same index may appear in the list multiple times.
        dtype : BASIC_TYPE, optional
            The data type.
        alias : str, default ""
            Used to provide an alternative name for an entity in the UI.
            The value is used in place of the entity name where appropriate in the UI.
        format : str, default ""
            The formatting string used for displaying numeric values.
        hidden : Hidden, default Hidden.FALSE
            Indicates whether the UI should hide the entity where appropriate.
        manage : Manage, default Manage.INPUT
            How and whether Insight handles an entity. Defines how the system manages the entity data.
        read_only : bool, default False
            Whether an entity is readonly. Specifies that the value(s) of the entity cannot be modified. See also
            `hidden`.
        transform_labels_entity : str, default ""
            The name of an entity in the schema from which to read labels for values of this entity.
            The type of the index set of the labels entity must match the data type of this entity.
            The data type of the labels entity can be any primitive type.
        update_after_execution : bool, default False
            Whether the value of the entity in the scenario is updated with the value of
            the corresponding model entity at the end of the scenario execution.
            If `True` the value of the entity is updated to correspond with the model entity after execution.
        update_keep_result_data : bool, default False
            Whether to retain result data when this input entity is updated outside a scenario execution
            (e.g. in a view or a REST API call).
            If `False`, the result data may be deleted when a view or REST API request updates this entity, depending on
            the configuration of :fct-ref:`AppConfig.result_data`.
            If `True`, the result data will not be deleted when this entity is updated.
        update_progress : bool, default False
            Whether the value of the entity in the scenario is sent on progress updates.
            If `True` the value of the entity will be written back to the Insight repository when
            :fct-ref:`insight.send_progress_update` is called from an execution mode where the `send_progress`
            attribute is `True`.
        entity_name : str, optional
            The entity name. If not given, the name of the class attribute will be used instead.
            Only valid for entities in a `ScenarioData`-decorated class.
        series_name : str, optional
            The name to use for the values in the resultant series. If not given, the entity name will
            be used.
            Only valid for entities in a `ScenarioData`-decorated class.
        index_types : List[BASIC_TYPE], optional
            The types of the columns to use for the index(es) in the resultant series.
            Only valid for entities in an `ScenarioData`-decorated class, where it is optional.

        Notes
        -----
        Parameters before `update_progress` can be specified positionally for reasons of backwards compatibility,
        but it's recommended that you always use named arguments if you're specifying parameters other than `index`,
        `dtype` and `alias`.
        """

        #
        #
        self.__series_name = series_name

        Entity.__init__(
            self,
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
        IndexedPandas.__init__(
            self,
            index=index,
            index_types=index_types
        )

    def _init_app_entity(self, entities: Mapping[str, EntityBase]):
        Entity._init_app_entity(self, entities)
        IndexedPandas._init_app_entity(self, entities)

    def _check_valid_app_entity(self):
        Entity._check_valid_app_entity(self)
        IndexedPandas._check_valid_app_entity(self)

        #
        if self.__series_name:
            raise TypeError(f'Series entity "{self.name}" must not set the "series_name" attribute.')

    def _check_valid_scenario_data_entity(self):
        Entity._check_valid_scenario_data_entity(self)
        IndexedPandas._check_valid_scenario_data_entity(self)

    @property
    def type_hint(self) -> type:
        """
        The target Python type for values in this Insight entity - e.g. the Python target type of an
        `xpressinsight.Series` is a `pandas.Series`.
        """
        return pd.Series

    @property
    def series_name(self) -> Optional[str]:
        """ Name to be used for this Pandas series. """
        return self.__series_name if self.__series_name else self.name

    @property
    def _has_result_values(self) -> bool:
        return self.manage == Manage.RESULT

    @property
    def _has_keep_result_data_values(self) -> bool:
        return self.update_keep_result_data

    @override
    def check_value(self, value: Any,
                    columns: Iterable = None,
                    *,
                    allow_duplicate_indices=False):
        """ Verifies that the given value can be used as the value of an entity of this type. """
        #
        if not isinstance(value, pd.Series):
            raise TypeError(f"""
            Problem with entity "{self.name}":
                Expected: pandas Series
                Actual: {type(value)}.
            """)

        #
        self._check_valid_index(value, allow_duplicate_indices=allow_duplicate_indices)

        #
        if self.dtype:
            check_type_np(value.values, self.dtype, self.name)
