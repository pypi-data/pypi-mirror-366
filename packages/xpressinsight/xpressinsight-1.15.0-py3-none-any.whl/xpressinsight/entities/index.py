"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Define the Index entity type.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2025 Fair Isaac Corporation. All rights reserved.
"""
from abc import abstractmethod, ABC
from packaging import version
import sys
from typing import Any, Tuple, Mapping, List, Iterable, Set, Optional, Union
from warnings import warn

import pandas as pd

from .basic_types import BASIC_TYPE, boolean, integer, string, real, check_type_np, check_type_pl, \
    BASIC_PANDAS_DTYPE_MAP
from .entity import Entity, EntityBase, Hidden, Manage
from ..type_checking import validate_optional_list
from .. import polars_shims as pl

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override



def check_index_type_value(value: Any, expected_dtype: Optional[BASIC_TYPE], name: str):
    """ Check the value of Pandas index is as expected. This may be called for an Index entity value or for an
        an index level in a Pandas Series or DataFrame. ."""
    if not isinstance(value, pd.Index):
        raise TypeError(f"""
        Problem with {name}:
            Expected: pandas.Index
            Actual: {type(value)}.
        """)

    if value.size == 0:
        return

    if expected_dtype == integer:
        #
        if not pd.api.types.is_integer_dtype(value.dtype):
            msg = f"""
            All values in {name} must be integers, but the data type is: {value.dtype}.
            """
            raise TypeError(msg)

        check_type_np(value.values, integer, name)

    elif expected_dtype == real:
        check_type_np(value.values, real, name)

    elif expected_dtype == string:
        check_type_np(value.values, string, name)

    elif expected_dtype == boolean:
        if not pd.api.types.is_bool_dtype(value):
            msg = f"""
            All values in {name} must be Booleans.
            """
            raise TypeError(msg)

    elif expected_dtype:
        raise ValueError(f"Unrecognized dtype: {expected_dtype}")


def check_polars_index_type_value(value: Any, expected_dtype: Optional[BASIC_TYPE], name: str):
    """ Check the values in a Polars series are valid for a Polars index column - this may be called for
        a PolarsIndex entity value or for an index column in a PolarsDataFrame entity. """
    if not isinstance(value, pl.Series):
        raise TypeError(f"""
        Problem with {name}:
            Expected: polars.Series
            Actual: {type(value)}.
        """)

    if expected_dtype:
        check_type_pl(value, expected_dtype, name)

    #
    #
    if value.has_nulls() if pl.polars_version >= version.parse('0.20.28') else value.null_count() > 0:
        raise TypeError(f"""
        Problem with {name}:
            An index must not contain NULL values.
        """)


def report_duplicates_found(allow_duplicate_indices: Optional[bool], message: str):
    """
    When duplicate index entries are found in am entity value, take appropriate action for the value of
    allow_duplicate_indices - raise `KeyError` if False, a `RuntimeWarning` if None, or do nothing if `True`.
    """
    if allow_duplicate_indices is False:
        raise KeyError(message)

    if allow_duplicate_indices is None:
        warn(category=RuntimeWarning,
             message=message + "\nFrom xpressinsight 1.16 onwards, this will be an error unless "
                               "`allow_duplicate_indices` is set to `True` in the `AppConfig` decorator; you can "
                               "also set `allow_duplicate_indices=False` to make this the current behavior.")


class IndexBase(Entity, ABC):
    """
    Abstract base class for entities that will be represented as sets in the Insight schema.  An index-type entity
    contains an unordered collection of unique values.

    See Also
    --------
    Index
    PolarsIndex
    """
    def __init__(self,
                 dtype: BASIC_TYPE = None,
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
                 entity_name: str = None):
        """
        Create a new IndexBase entity.

        Parameters
        ----------
        dtype : BASIC_TYPE
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

        Notes
        -----
        Parameters before `update_progress` can be specified positionally for reasons of backwards compatibility,
        but it's recommended that you always use named arguments if you're specifying parameters other than
        `dtype` and `alias`.
        """
        #
        if dtype == real:
            raise TypeError('An Index entity cannot have type "real".')

        super().__init__(dtype=dtype,
                         alias=alias,
                         format=format,
                         hidden=hidden,
                         manage=manage,
                         read_only=read_only,
                         transform_labels_entity=transform_labels_entity,
                         update_after_execution=update_after_execution,
                         update_keep_result_data=update_keep_result_data,
                         update_progress=update_progress,
                         entity_name=entity_name)

        #
        self._indexed_entity_names: Set[str] = set()


class Index(IndexBase):
    """
    The configuration of an *index* entity, to be stored as a Pandas `Index`. Use the helper function
    `xpressinsight.types.Index` to declare an index entity in an app, rather than instantiating `xpressinsight.Index`
    directly.

    Notes
    -----
    In older versions of `xpressinsight`, it was possible to use the `Index` as the annotation for an entity.
    This syntax is now deprecated and should not be used in new apps; it will not be supported in Python 3.12 and
    above.

    See Also
    --------
    types.Index
    Series
    DataFrame
    """

    #
    #
    # noinspection PyShadowingBuiltins
    # pylint: disable-next=too-many-arguments
    def __init__(self,
                 dtype: BASIC_TYPE = None,
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
                 entity_name: str = None):
        """
        Create a new Index entity.

        Parameters
        ----------
        dtype : BASIC_TYPE
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

        Notes
        -----
        Parameters before `update_progress` can be specified positionally for reasons of backwards compatibility,
        but it's recommended that you always use named arguments if you're specifying parameters other than
        `dtype` and `alias`.
        """
        super().__init__(dtype=dtype,
                         alias=alias,
                         format=format,
                         hidden=hidden,
                         manage=manage,
                         read_only=read_only,
                         transform_labels_entity=transform_labels_entity,
                         update_after_execution=update_after_execution,
                         update_keep_result_data=update_keep_result_data,
                         update_progress=update_progress,
                         entity_name=entity_name)

    @property
    def type_hint(self) -> type:
        """
        The target Python type for values in this Insight entity - e.g. the Python target type of an
        `xpressinsight.Index` is a `pandas.Index`.
        """
        return pd.Index

    @override
    def check_value(self, value: Any,
                    columns: Iterable = None,
                    *,
                    allow_duplicate_indices=False):
        check_index_type_value(value, self.dtype, self.name)

        #
        if not allow_duplicate_indices:
            if value.has_duplicates:
                duplicates_mask = value.duplicated(keep=False)
                report_duplicates_found(allow_duplicate_indices=allow_duplicate_indices, message=f"""
                    Problem with entity "{self.name}":
                        Expected: Index with unique values
                        Actual: Duplicate value "{value[duplicates_mask][0]}".
                    """)


class PolarsIndex(IndexBase):
    """
    The configuration of an *index* entity, to be represented as a Polars Series. Use the helper function
    `xpressinsight.types.PolarsIndex` to declare an index entity in an app, rather than instantiating
    `xpressinsight.PolarsIndex` directly.

    Notes
    -----
    In an Insight app schema, an index is a sequence of unique values. As Polars does not have this concept, we
    represent the index as a Series.  The uniqueness of values in the series will be checked when the data is
    saved at the end of the scenario execution.

    Polars-type entities will only be available if `polars` has been installed in your Python environment.

    See Also
    --------
    types.PolarsIndex
    PolarsDataFrame
    """

    #
    #
    # noinspection PyShadowingBuiltins
    # pylint: disable-next=too-many-arguments
    def __init__(self,
                 dtype: BASIC_TYPE = None,
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
                 entity_name: str = None):
        """
        Create a new Index entity.

        Parameters
        ----------
        dtype : BASIC_TYPE
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

        Notes
        -----
        Parameters before `update_progress` can be specified positionally for reasons of backwards compatibility,
        but it's recommended that you always use named arguments if you're specifying parameters other than
        `dtype` and `alias`.
        """
        pl.check_polars_available()
        super().__init__(dtype=dtype,
                         alias=alias,
                         format=format,
                         hidden=hidden,
                         manage=manage,
                         read_only=read_only,
                         transform_labels_entity=transform_labels_entity,
                         update_after_execution=update_after_execution,
                         update_keep_result_data=update_keep_result_data,
                         update_progress=update_progress,
                         entity_name=entity_name)

    @property
    def type_hint(self) -> type:
        """
        The target Python type for values in this Insight entity - e.g. the Python target type of an
        `xpressinsight.PolarsIndex` is a `polars.Series`.
        """
        return pl.Series

    @override
    def check_value(self, value: Any,
                    columns: Iterable = None,
                    *,
                    allow_duplicate_indices: Optional[bool] = None):
        check_polars_index_type_value(value, self.dtype, self.name)

        #
        if not allow_duplicate_indices:
            duplicates_mask = value.is_duplicated()
            if duplicates_mask.any():
                duplicate_values = value.filter(duplicates_mask)

                report_duplicates_found(allow_duplicate_indices=allow_duplicate_indices, message=f"""
                    Problem with entity "{self.name}":
                        Expected: Polars Series with unique values
                        Actual: Duplicate value "{duplicate_values[0]}".
                    """)


def get_index_level_names(index_entity_names: Iterable[str]) -> List[str]:
    """
    Generate a unique name for each index level. The level name for an index will be the name of the index entity
    unless the same index entity is used in multiple levels, in which case duplicate names will be decorated with the
    level number (e.g. ".2", ".3").
    """
    levels_with_names: List[str] = []
    names_used_so_far: Set[str] = set()

    for name in index_entity_names:
        if name in names_used_so_far:
            name_with_level = f"{name}.{len(levels_with_names) + 1}"
        else:
            name_with_level = name

        levels_with_names.append(name_with_level)
        names_used_so_far.add(name_with_level)

    return levels_with_names


class Indexed(ABC):
    """
    Class implementing functionality common to all entity types that have indexes (Series, DataFrame, etc.).
    As not all of these classes have the same superclass (some extend Entity, some EntityBase), the Indexed class
    does not extend any of these.
    """
    def __init__(
            self,
            index: Optional[Union[str, List[str]]] = None,
            index_types: Optional[List[BASIC_TYPE]] = None
    ):
        """
        Initializes the index-related parts of this class.

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
        index_types : Optional[List[BASIC_TYPE]] = None
            The types of the columns to use for the index(es) in the resultant series.
            Only valid for entities in an `ScenarioData`-decorated class, where it is optional.
        """
        self.__index_names = validate_optional_list(self, 'index', str, 'string', index)
        self.__index_types = validate_optional_list(self, 'index_types', BASIC_TYPE, 'BASIC_TYPE', index_types)
        self.__index: Optional[Tuple[Index, ...]] = None

    @property
    @abstractmethod
    def name(self) -> str:
        """ Name of the attribute representing the entity. """
        raise RuntimeError("Subclass should have overridden 'name' property")

    def __get_index_tuple(self, index_names: Tuple[str, ...], entities: Mapping[str, EntityBase]
                          ) -> Tuple[IndexBase, ...]:
        """ Get a Tuple of Index objects from a single or tuple of index entity names. """
        result: List[IndexBase] = []

        for index_name in index_names:
            index = entities.get(index_name, None)

            if isinstance(index, IndexBase):
                result.append(index)
            else:
                err_msg = f'Invalid index "{index_name}" for xpressinsight.{type(self).__name__} "{self.name}".'
                if index is None:
                    err_msg += f' Entity "{index_name}" not declared.'
                else:
                    err_msg += (f' Entity "{index_name}" is a {type(index)}, but must be an xpressinsight.Index'
                                f' or xpressinsight.PolarsIndex.')
                raise KeyError(err_msg)

        return tuple(result)

    def _init_app_entity(self, entities: Mapping[str, EntityBase]):
        if self.__index is not None:
            raise RuntimeError(f'The {type(self).__name__} "{self.name}" has already been initialized.')

        if self.__index_names is not None:
            self.__index = self.__get_index_tuple(self.__index_names, entities)
            for idx in self.__index:
                idx._indexed_entity_names.add(self.name)

    @property
    @abstractmethod
    def _has_result_values(self) -> bool:
        """ Query whether this entity is manage=RESULT, or this is a dataframe with some columns that are
        manage=RESULT. """
        raise RuntimeError(f"Please implement {type(self)._has_result_values}")

    @property
    @abstractmethod
    def _has_keep_result_data_values(self) -> bool:
        """ Query whether this entity is keep_result_data=True, or this is a dataframe with some columns that are
        keep_result_data=RESULT. """
        raise RuntimeError(f"Please implement {type(self)._has_keep_result_data_values}")

    def _check_valid_app_entity(self):
        #
        if not self.__index_names:
            raise TypeError(f'{type(self).__name__} entity "{self.name}" must have index names.')

        #
        if self.__index_types:
            raise TypeError(f'{type(self).__name__} entity "{self.name}" must not set the "index_types" attribute.')

        #
        if self._has_result_values and self.index and any(idx.update_keep_result_data for idx in self.index):
            raise TypeError(f'{type(self).__name__} entity "{self.name}" cannot have indexes with '
                            f'the "update_keep_result_data" attribute set to `True` if it contains result data.')

        #
        #
        #
        #
        if (self._has_keep_result_data_values and not all(idx.update_keep_result_data for idx in self.index) and
                (len(self.index) > 1 or len(self.index[0]._indexed_entity_names) > 1)):
            raise TypeError(f'{type(self).__name__} entity "{self.name}" must have the "update_keep_result_data" '
                            f'attribute set to `True` on all its indexes.')

    def _check_valid_scenario_data_entity(self):
        #
        if self.__index_names and self.__index_types and len(self.__index_names) != len(self.__index_types):
            raise TypeError(f'{type(self).__name__} entity "{self.name}" must not specify different numbers of index '
                            'names and types.')

    @abstractmethod
    def _check_valid_index(self, value: Any, allow_duplicate_indices: Optional[bool]):
        """ Given a value for the entity, check that the indexes of that value are suitable. """

    @property
    def index(self) -> Optional[Tuple[IndexBase, ...]]:
        """ Index entities for this entity. """
        return self.__index

    @property
    def index_names(self) -> Optional[Tuple[str, ...]]:
        """ Index entity names for this entity. """
        return self.__index_names

    @property
    def unique_index_names(self) -> Optional[List[str]]:
        """
        Index names, modified so that each is unique. Where an entity is indexed multiple times by the same index,
        duplicate names will be decorated with their index (e.g. ".2", ".3"). This will correspond to the labels
        of the indexes in the actual series or data frame.
        """
        return get_index_level_names(self.index_names) if self.index_names else None

    @property
    def index_types(self) -> Optional[Tuple[BASIC_TYPE, ...]]:
        """ Index types for this series. """
        if self.__index_types:
            return self.__index_types

        if self.index:
            #
            #
            dtypes: List[BASIC_TYPE] = []
            for ind in self.index:
                if not ind.dtype:
                    raise ValueError(f"No type configured for index entity {ind.name}")

                dtypes.append(ind.dtype)

            return tuple(dtypes)

        return None


class IndexedPandas(Indexed, ABC):
    """
    Class implementing functionality common to Pandas entity types that have indexes (Series, DataFrame, etc.).
    """

    def _check_valid_index(self, value: Union[pd.Series, pd.DataFrame], allow_duplicate_indices: Optional[bool]):
        """ Check the types and content of the indexes of the Pandas series or data-frame. """

        if self.index_names and len(self.index_names) != value.index.nlevels:
            raise TypeError(f'Problem with entity "{self.name}": dimension of index set is {value.index.nlevels} '
                            f'but expecting {len(self.index_names)}.')

        if self.index_types:
            index_names = self.index_names or ["unnamed" for _typ in self.index_types]

            for idx_id, (idx_name, idx_dtype) in enumerate(zip(index_names, self.index_types)):
                check_index_type_value(value.index.get_level_values(idx_id), idx_dtype,
                                       f'index {idx_id + 1} ("{idx_name}") of entity "{self.name}"')

        #
        if not allow_duplicate_indices and value.index.has_duplicates:
            duplicates_mask = value.index.duplicated(keep=False)
            first_duplicate = value.index[duplicates_mask][0]
            if isinstance(value.index, pd.MultiIndex):
                index_tuple = f"({', '.join(str(v) for v in first_duplicate)})"
            else:
                index_tuple = f"({first_duplicate})"
            report_duplicates_found(allow_duplicate_indices=allow_duplicate_indices, message=f"""
                Problem with entity "{self.name}":
                    Expected: {value.__class__.__name__} with unique index tuples
                    Actual: Duplicate entries for index {index_tuple}.
                """)

    def _get_empty_index(self) -> pd.Index:
        """ Creates an empty pandas Index or MultiIndex with name and dtype (if available) information. """
        if self.index_names is None:
            raise RuntimeError(f'Unable to create empty pandas Index for entity "{self.name}"; entity\'s index names '
                               f'are not available')

        if self.index_types:
            #
            index_list = [
                pd.Index([], dtype=BASIC_PANDAS_DTYPE_MAP[index_type], name=level_name)
                for (level_name, index_type) in zip(get_index_level_names(self.index_names), self.index_types)
            ]
        else:
            #
            index_list = [pd.Index([], name=level_name) for level_name in get_index_level_names(self.index_names)]

        if len(index_list) == 1:
            pd_index = index_list[0]
        else:
            pd_index = pd.MultiIndex.from_product(index_list)

        return pd_index
