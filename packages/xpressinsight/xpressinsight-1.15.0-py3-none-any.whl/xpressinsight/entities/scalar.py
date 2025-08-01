"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Define the classes for representing scalar and param entities.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""

from typing import Type, Union, Any, Iterable, Optional
import sys

from .basic_types import (BASIC_TYPE_VALUE, BasicType, boolean, integer, string, real, check_basic_type_value,
                          SCALAR_DEFAULT_VALUES, BASIC_TYPE_MAP)
from .entity import Entity, Hidden, Manage

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override


class ScalarBase(Entity):
    """ Base superclass for scalar-type entities (Scalar and Param). """
    #
    #
    # noinspection PyShadowingBuiltins
    # pylint: disable-next=too-many-arguments
    def __init__(
            self,
            default: BASIC_TYPE_VALUE = None,
            dtype: Type[BasicType[BASIC_TYPE_VALUE]] = None,
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
        default : BASIC_TYPE_VALUE, optional
            The default value; if specified, must be a value of the appropriate type for the `dtype` of this entity
            (e.g. a `str` if `dtype` is `string`).
        dtype : Type[BasicType[BASIC_TYPE_VALUE]]
            The data type; one of `boolean`, `real`, `integer` or `string`.
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
        but it's recommended that you always use named arguments if you're specifying parameters other than `default`,
        `dtype` and `alias`.
        """
        #
        if dtype is None and default is not None:
            #
            if isinstance(default, str):
                dtype = string
            elif isinstance(default, bool):
                dtype = boolean
            elif isinstance(default, int):
                dtype = integer
            elif isinstance(default, float):
                dtype = real
            else:
                raise TypeError(f'The default value of a scalar or parameter must be a str, int, bool, '
                                f'or float, but it is a "{type(default)}".')

        #
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

        if default is None and self.dtype is not None:
            self.__default = SCALAR_DEFAULT_VALUES[dtype]
            assert self.__default is not None
        elif default is not None:
            self.check_value(default)
            self.__default = default
        else:
            self.__default = None

    def _check_valid_app_entity(self):
        if self.default is None and self.dtype is None:
            raise TypeError(f'Entity "{self.name}" must specify at least one of the following parameters: '
                            'dtype (data type), default (default value).')

        super()._check_valid_app_entity()

    @property
    def type_hint(self) -> type:
        """
        The target Python type for values in this Insight entity - e.g. the Python target type of an
        `xpressinsight.Series` is a `pandas.Series`.
        """
        return BASIC_TYPE_MAP.get(self.dtype)

    @override
    def check_value(self, value: Any,
                    columns: Iterable = None,
                    *,
                    allow_duplicate_indices=False):
        """ Check if the type is correct and check the bounds. """
        check_basic_type_value(self.dtype, value, self.name)

    @property
    def default(self) -> Union[str, int, bool, float]:
        """ Default value for this scalar. """
        return self.__default


class Scalar(ScalarBase):
    """
    The configuration of a *scalar* entity. Rather than instantiating `xpressinsight.Scalar` directly, you should
    use the helper function `xpressinsight.types.Scalar` or `xpressinsight.data.Scalar` to declare a scalar entity in
    an app or scenario data container, as appropriate.

    Notes
    -----
    In older versions of `xpressinsight`, it was possible to use the `Scalar` as the annotation for an entity.
    This syntax is now deprecated and should not be used in new apps; it will not be supported in Python 3.12 and
    above.

    See Also
    --------
    types.Scalar
    data.Scalar
    Param
    """


class Param(ScalarBase):
    """
    The configuration of a *parameter* entity. Parameters can be used to configure an Xpress Insight app. When
    parameters are declared, their name, data type, and default value must be specified. Parameters are typically
    read-only. Use the helper function `xpressinsight.types.Param` to declare a parameter entity in an app, rather than
    instantiating `xpressinsight.Param` directly.

    Notes
    -----
    In older versions of `xpressinsight`, it was possible to use the `Param` as the annotation for an entity.
    This syntax is now deprecated and should not be used in new apps; it will not be supported in Python 3.12 and
    above.

    See Also
    --------
    types.Param
    Scalar
    """

    def __init__(
            self,
            default: BASIC_TYPE_VALUE = None,
            dtype: Type[BasicType[BASIC_TYPE_VALUE]] = None,
            entity_name: Optional[str] = None,
    ):
        """
        Initializes `Param` with the data type or a default value (in which case data type is inferred).

        Parameters
        ----------
        default : BASIC_TYPE_VALUE, optional
            The default value; if specified, must be of the appropriate value for the `dtype` of this entity (e.g.
            a `str` if `dtype` is `string`).
        dtype : Type[BasicType[BASIC_TYPE_VALUE]], optional
            The data type; one of `boolean`, `real`, `integer` or `string`.
        entity_name : str, optional
            The entity name. If not given, the name of the class attribute will be used instead.
            For a parameter-type entity, the "entity name" will be the name of the parameter.
            Only valid for entities in a `ScenarioData`-decorated class.
        """

        super().__init__(
            default,
            dtype=dtype,
            entity_name=entity_name
        )
