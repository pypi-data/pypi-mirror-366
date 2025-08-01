"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Define the various classes for representing the app's schema.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2025 Fair Isaac Corporation. All rights reserved.
"""

#
from abc import ABC, abstractmethod

import sys
from typing import (Any, Optional, Mapping, Iterable)

from deprecated import deprecated

from .basic_types import BASIC_TYPE, BasicType
from ..mosel import validate_ident, validate_annotation_str

from ..type_checking import check_instance_attribute_types, XiEnum

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self

ENTITY_CLASS_NAMES = {'Param', 'Scalar', 'Index', 'Series', 'DataFrame', 'Column', 'PolarsIndex', 'PolarsDataFrame'}


class Manage(XiEnum):
    """
    How and whether Insight handles an entity.

    When not specified in an entity declaration, the entity will typically be handled as `INPUT`.

    Attributes
    ----------
    INPUT : str
        Included in the scenario input data.
    RESULT : str
        Included in the scenario results data.

    Examples
    --------
    Manage a scalar entity as an input

    >>> MyInteger: xi.types.Scalar(dtype=xi.integer,
    ...                            alias='My Integer',
    ...                            manage=xi.Manage.INPUT)
    """

    INPUT = "input"
    RESULT = "result"


class Hidden(XiEnum):
    """
    Possible values of whether the UI should hide an entity where appropriate.

    Attributes
    ----------
    ALWAYS : str
        Indicates that the UI should hide the entity always.
    TRUE : str
        Indicates that the UI should hide the entity where appropriate.
    FALSE : str
        Indicates that the UI should show the entity where appropriate.

    Examples
    --------
    Always hide an entity in the Insight UI

    >>> MyInteger: xi.types.Scalar(dtype=xi.integer,
    ...                            alias='My Integer',
    ...                            hidden=xi.Hidden.ALWAYS)
    """

    ALWAYS = "always"
    TRUE = "true"
    FALSE = "false"


class UnexpectedEntityTypeError(TypeError):
    """ Specialization of TypeError used in cases where we have an entity object that is not of an expected type.
        This may because the object is of a different entity type (e.g. `Param` in code that expected `Series`
        or `DataFrame`, or the object is not an entity at all. """

    def __init__(self, entity: Any):
        """ Create an error for the case where 'entity' is either not an entity or a type of entity not expected by
            this code. """
        entity_name_or_string = entity.name if (hasattr(entity, "name") and entity.name) else str(entity)
        super().__init__(f'Unexpected type "{type(entity).__name__}" for entity "{entity_name_or_string}".')


class EntityBase(ABC):
    """
    Abstract base class of all Insight entities, including composed entities like *DataFrames*.

    See Also
    --------
    AppConfig.entities
    """
    __name: str

    def __init__(self):
        self.__name = ''

    def _init_app_entity(self, entities: Mapping[str, Self]):
        """ Initialize this entity, creating links to other entities as given. """

    @property
    def name(self) -> str:
        """ Name of the attribute representing the entity. """
        return self.__name

    @name.setter
    def name(self, name: str):
        if self.__name == '':
            self.__name = validate_ident(name, type(self).__name__, 'name')
        else:
            raise AttributeError(f'Cannot set name of {type(self).__name__} to "{name}" '
                                 f'because it has already been initialized to "{self.__name}".')

    @property
    @abstractmethod
    def update_progress(self) -> bool:
        """ Whether this is a 'progress' entity. """

    @abstractmethod
    def is_managed(self, manage: Manage) -> bool:
        """ Query whether this entity would be managed as input / result. """

    @property
    @abstractmethod
    def type_hint(self) -> type:
        """
        The target Python type for values in this Insight entity - e.g. the Python target type of an
        `xpressinsight.Series` is a `pandas.Series`.
        """

    @deprecated(version='1.14.0', reason='Use `check_value` function instead')
    def check_type(self, value: Any, columns: Optional[Iterable] = None):
        """ Verifies that the given value can be used as the value of an entity of this type. This function
        is deprecated, code should use :fct-ref:`check_value` instead.  """
        self.check_value(value, columns=columns, allow_duplicate_indices=True)

    def check_value(self, value: Any,
                    columns: Optional[Iterable] = None,
                    *,
                    allow_duplicate_indices: Optional[bool] = None):
        """
        Verifies that the given value can be used as the value of an entity of this type.

        Parameters
        ----------
        value : Any
            The potential value for this entity.
        columns : Iterable[Column]
            If this is a DataFrame-type entity, an iterable specifying a subset of the columns to check;
            checks all columns if unset. Ignored for entity types that don't have columns.
        allow_duplicate_indices : bool, optional
            Whether to allow duplicate indices in the entity. If `False`, a `KeyError` is raised when a duplicate
            index tuple is found in a `Series`, `DataFrame` or `PolarsDataFrame` entity, or a duplicate value in
            an `Index` or `PolarsIndex` entity. If `None`, a warning will be output if a duplicate is detected. If
            `True`, this function will not check for duplicates.

        Raises
        ------
        TypeError
            If the value has the wrong type for this entity.
        KeyError
            If there is an issue with the indexing of the value.
        ValueError
            If the value is in some other way not acceptable for this entity.
        """

    def _check_valid_app_entity(self):
        """ Verifies that this entity is valid for use in an app. """

    def _check_valid_scenario_data_entity(self):
        """ Verifies that this entity is valid for use in a ScenarioData container. """


#
#
# pylint: disable-next=too-many-instance-attributes
class Entity(EntityBase, ABC):
    """
    Abstract base class of all native Insight entities, excluding composed entities like *DataFrames*. This class
    is used both for entities of the current app in classes decorated with `AppConfig` and entities defined for
    scenario data in classes decorated with `ScenarioData`.
    """

    __dtype: Optional[BASIC_TYPE]
    __alias: str
    __format: str
    __hidden: Hidden
    __manage: Manage
    __read_only: bool
    __transform_labels_entity: str
    __update_after_execution: bool
    __update_keep_result_data: bool
    __update_progress: bool
    __entity_name: Optional[str]

    #
    #
    # noinspection PyShadowingBuiltins
    # pylint: disable-next=too-many-arguments
    def __init__(self,
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
                 entity_name: str = None
                 #
                 ):
        """
        The constructor.

        Parameters
        ----------
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
        entity_name : str = None
            The entity name. If not given, the name of the class attribute will be used instead.
            Only necessary if the name of the entity in the Insight schema differs from the name of the class
            attribute.

        Notes
        -----
        Parameters before `update_progress` can be specified positionally for reasons of backwards compatibility,
        but it's recommended that you always use named arguments if you're specifying parameters other than
        `dtype` and `alias`.
        """
        super().__init__()
        self.__dtype = dtype
        #
        self.__alias = alias
        self.__format = format
        self.__hidden = hidden
        self.__manage = manage
        self.__read_only = read_only
        self.__transform_labels_entity = transform_labels_entity.replace('.', '_')
        self.__update_after_execution = update_after_execution
        self.__update_keep_result_data = update_keep_result_data
        self.__update_progress = update_progress
        self.__entity_name = entity_name
        #
        check_instance_attribute_types(self)
        validate_annotation_str(alias, 'entity alias')
        validate_annotation_str(format, 'entity format')

        if transform_labels_entity != "":
            validate_ident(self.__transform_labels_entity, "transform labels entity")

        #
        #
        #
        if update_after_execution and manage == Manage.RESULT:
            raise ValueError('Cannot set parameter update_after_execution to True for a result entity. '
                             'This parameter is only valid for input entities.')

        if update_keep_result_data and manage == Manage.RESULT:
            raise ValueError('Cannot set parameter update_keep_result_data to True for a result entity. '
                             'This parameter is only valid for input entities.')

        if update_progress and manage == Manage.INPUT and not update_after_execution:
            raise ValueError('Cannot set parameter update_progress to True for an input entity if '
                             'update_after_execution is not also True.')

        if dtype and not issubclass(dtype, BasicType):
            raise TypeError('dtype of entity  must be a subclass of BasicType.')

    @property
    def dtype(self) -> Optional[BASIC_TYPE]:
        """ The type of values in this entity. """
        return self.__dtype

    @property
    def alias(self) -> str:
        """ Alias to use for the entity in the UI. """
        return self.__alias

    @property
    def format(self) -> str:
        """ Format string for entity values. """
        return self.__format

    @property
    def hidden(self) -> Hidden:
        """ Whether the entity is hidden. """
        return self.__hidden

    @property
    def manage(self) -> Manage:
        """ How the entity is managed. """
        return self.__manage

    @property
    def read_only(self) -> bool:
        """ Whether the entity can be edited from the UI. """
        return self.__read_only

    @property
    def transform_labels_entity(self) -> str:
        """ Name of labels transformation series for this entity. """
        return self.__transform_labels_entity

    @property
    def update_after_execution(self) -> bool:
        """ Whether this input entity is also saved with results. """
        return self.__update_after_execution

    @property
    def update_keep_result_data(self) -> bool:
        """ Whether to retain the result data when the value of this entity is updated outside a scenario
        execution. """
        return self.__update_keep_result_data

    @property
    def update_progress(self) -> bool:
        return self.__update_progress

    def is_managed(self, manage: Manage) -> bool:
        """ Check whether the entity is managed as the given management type: input/result. """
        return self.__manage == manage or (self.__update_after_execution and manage == Manage.RESULT)

    @property
    def entity_name(self) -> str:
        """ Name of the entity. """
        return self.__entity_name if self.__entity_name else self._default_entity_name

    @property
    def _default_entity_name(self) -> str:
        """ Entity name to use if none is specified in `entity_name` attribute. """
        return self.name

    @property
    def _allow_non_default_entity_name_in_app(self) -> bool:
        """ Whether to allow an app to set the entity name to a non-default value for this type """
        return False

    def _check_valid_app_entity(self):
        super()._check_valid_app_entity()

        #
        #
        #
        if self.__entity_name is not None:
            validate_ident(self.__entity_name, "entity name")

        #
        if not self._allow_non_default_entity_name_in_app and self.entity_name != self._default_entity_name:
            raise TypeError(f'App entity "{self.name}" cannot have an entity name different from the attribute name.')

        #
        if self.dtype is None:
            raise TypeError(f'No "dtype" was configured for entity {self.name}.')
