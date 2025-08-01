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

import inspect
import sys
from abc import ABC
from copy import deepcopy
from types import MappingProxyType
from typing import Annotated, Any, Dict, Optional, Mapping, ValuesView, Type, Callable, Union, Iterable, \
    get_args, get_type_hints, get_origin

from .entities import ENTITY_CLASS_NAMES, ScalarBase, DataFrameBase, EntityBase, Entity, Manage, \
    get_non_composed_entities_from_names, get_non_composed_entities


class EntitiesConfig(ABC):
    """
    Abstract base class for entity container configuration. An entity container (such as `AppConfig` or
    `ScenarioData`) is used on classes that will contain Insight entity data, written to attributes identified by
    annotations (e.g. `types.Scalar`).
    """

    def __init__(self):
        self.__entities: Dict[str, EntityBase] = {}

    def __init_entity_names(self):
        """ Assign a name to all entities (except for Columns).
            The name assignment also checks whether the names are valid the identifiers. """
        for entity_name, entity in self.__entities.items():
            entity.name = entity_name

    @staticmethod
    def __check_no_entity_class_attributes(data_cls: Type, recommended_annotation_prefix: str) -> None:
        """
        Verify that neither the given `data_cls` nor its superclasses declare any class attributes with Insight
        entity types (developer accidentally typed `=` instead of `:`),
        e.g. `entity_name = xi.types.Scalar(dtype=xi.real)`
        """
        public_class_attributes = [(name, value) for (name, value) in inspect.getmembers(data_cls)
                                   if not name.startswith('_')]
        for (name, value) in public_class_attributes:
            if (isinstance(value, EntityBase) or
                    (get_origin(value) is Annotated and any(x for x in get_args(value) if isinstance(x, EntityBase)))):
                raise TypeError(f'Class attribute "{name}" in "{data_cls.__name__}" has type of an Insight entity.\n'
                                f'Insight entities must be declared as instance attributes, e.g.:\n'
                                f'    my_entity_name: {recommended_annotation_prefix}.Scalar(dtype=xi.integer)\n'
                                f'and not:\n'
                                f'    my_entity_name = {recommended_annotation_prefix}.Scalar(dtype=xi.integer)')

    @staticmethod
    def __get_old_syntax_entity_annotation_strings(annotations: Dict[str, Any]) -> Dict[str, str]:
        """
        Return the dictionary of entities from the supplied annotation dictionary that use the 'old syntax'
        annotations such as `xpressinsight.Scalar` instead of `xpressinsight.types.Scalar`, provided the annotation
        dictionary is string-based (i.e. postponed evaluation of annotations is activated).
        """
        old_syntax_entities = {}

        for (name, ann) in annotations.items():
            #
            #
            #
            #
            if isinstance(ann, str) and (ann.startswith("xi.") or ann.startswith("xpressinsight.")):
                #
                ann_without_package = ann.split('.', 1)[1]

                if any(ann_without_package.startswith(ent_cls_name) for ent_cls_name in ENTITY_CLASS_NAMES):
                    old_syntax_entities[name] = ann

        return old_syntax_entities

    @staticmethod
    def __get_old_syntax_entity_annotations(annotations: Dict[str, Any]) -> Dict[str, EntityBase]:
        """
        Return the list of entity names from the supplied annotation dictionary that use the 'old syntax' annotations
        such as "xi.Scalar" instead of "xi.types.Scalar", provided the annotation dictionary is not string-based (i.e.
        postponed evaluation of annotations not activated).
        """
        #
        #
        return {name: entity for (name, entity) in annotations.items() if isinstance(entity, EntityBase)}

    @staticmethod
    def __get_entities_from_type_hints(app_type_hints: Dict[str, type]) -> Dict[str, EntityBase]:
        """
        Given the type hints for a class, extract the entities from annotations
        """
        entities = {}
        for (name, type_hint) in app_type_hints.items():
            #
            if get_origin(type_hint) is Annotated:
                #
                entities_from_annotated = [arg for arg in get_args(type_hint) if isinstance(arg, EntityBase)]
                if len(entities_from_annotated) > 1:
                    raise TypeError(
                        f'Entity {name} has multiple Insight entity annotations; an entity must have only a\n'
                        'single annotation argument with type subclassing EntityBase'
                    )

                if len(entities_from_annotated) == 1:
                    #
                    #
                    #
                    #
                    #
                    entity = deepcopy(entities_from_annotated[0])
                    entities[name] = entity

                    #
                    #
                    actual_type_hint = get_args(type_hint)[0]

                    if isinstance(entity, ScalarBase) and not entity.dtype:
                        #
                        pass
                    elif (not issubclass(actual_type_hint, entity.type_hint)) or \
                            (issubclass(actual_type_hint, bool) and entity.type_hint == int):
                        raise TypeError(f"Entity {name} has type hint {actual_type_hint} "
                                        f"but should be {entity.type_hint}.")

        return entities

    @staticmethod
    def __get_update_entity_syntax_message(entity_names, annotation_prefix: str):
        """
        Get an appropriate message to include in assertions telling people to use a function to create the annotations
        for their entities.
        """
        return (f"Please update the annotations of entities {', '.join(entity_names)} as follows:\n"
                f"    xi.Param becomes {annotation_prefix}.Param\n"
                f"    xi.Scalar becomes {annotation_prefix}.Scalar\n"
                f"    xi.Index becomes {annotation_prefix}.Index\n"
                f"    xi.Series becomes {annotation_prefix}.Series\n"
                f"    xi.DataFrame becomes {annotation_prefix}.DataFrame")

    @staticmethod
    def __get_entities(data_cls: Type, recommended_annotation_prefix='xi.types',
                       allow_old_syntax=True) -> Dict[str, EntityBase]:
        """
        Get the entities for the given class.

        Parameters
        ----------
        data_cls : Type
            The class that defines the entities.

        recommended_annotation_prefix : str
            The prefix for the recommended annotation functions to use for generating annotations for this class,
            e.g. "xi.types".

        allow_old_syntax : bool
            If true, allow the 'old' syntax of using the EntityBase subclasses directly as type hints in the
            limited case where all the entities defined in the container use this syntax.
        """

        #
        #
        annotations = getattr(data_cls, '__annotations__', {})
        old_syntax_entities = EntitiesConfig.__get_old_syntax_entity_annotations(annotations)

        if old_syntax_entities and not allow_old_syntax:
            raise TypeError(
                f"The class {data_cls.__name__} is using an unsupported syntax for specifying entities.\n" +
                EntitiesConfig.__get_update_entity_syntax_message(old_syntax_entities.keys(),
                                                                  recommended_annotation_prefix)
            )

        #
        #
        #
        old_syntax_entity_strings = EntitiesConfig.__get_old_syntax_entity_annotation_strings(annotations)
        if old_syntax_entity_strings:
            raise TypeError(
                f"The class {data_cls.__name__} is using an old syntax for specifying entities, which is not\n"
                f"supported when postponed evaluation of annotations is activated (see \n"
                f"https://peps.python.org/pep-0563), i.e. when script uses `from __future__ import annotations`).\n" +
                EntitiesConfig.__get_update_entity_syntax_message(old_syntax_entity_strings.keys(),
                                                                  recommended_annotation_prefix)
            )

        #
        app_type_hints = get_type_hints(data_cls, include_extras=True)
        entities = EntitiesConfig.__get_entities_from_type_hints(app_type_hints)

        #
        #
        #
        if entities and old_syntax_entities:
            raise TypeError(
                f"The class {data_cls.__name__} is declaring entities using inconsistent syntax; when some\n"
                f"entities are annotated with either `xi.types.EntityType` or `Annotated[type, xi.EntityType]`, the\n"
                f"entities { ', '.join(old_syntax_entities.keys())} cannot be annotated as `xi.EntityType` (where\n"
                f"EntityType is one of: Param, Scalar, Index, Series, DataFrame)"
            )

        #
        #
        #
        #
        #
        #
        if old_syntax_entities:
            if sys.version_info >= (3, 12):
                raise TypeError(
                    f"The class {data_cls.__name__} is using an old syntax for specifying entities, which is not\n"
                    f"supported when using Python 3.12 or later.\n" +
                    EntitiesConfig.__get_update_entity_syntax_message(old_syntax_entities.keys(),
                                                                      recommended_annotation_prefix)
                )

            if sys.version_info >= (3, 11):
                print(
                    f"WARNING: The class {data_cls.__name__} is using an old syntax for specifying entities,\n"
                    "which is deprecated in Python 3.11 and will not be supported in Python 3.12 or later.\n" +
                    EntitiesConfig.__get_update_entity_syntax_message(old_syntax_entities.keys(),
                                                                      recommended_annotation_prefix),
                    file=sys.stderr
                )

        #
        #
        for ancestor_class in [cls for cls in data_cls.mro() if cls != data_cls]:
            ancestor_annotations = getattr(ancestor_class, '__annotations__', {})
            ancestor_old_syntax_entities = EntitiesConfig.__get_old_syntax_entity_annotations(ancestor_annotations)
            ancestor_old_syntax_entity_strings = EntitiesConfig.__get_old_syntax_entity_annotation_strings(
                ancestor_annotations)

            if ancestor_old_syntax_entities or ancestor_old_syntax_entity_strings:
                entities_to_list_in_error = (ancestor_old_syntax_entities.keys() if ancestor_old_syntax_entities
                                             else ancestor_old_syntax_entity_strings.keys())

                #
                #
                if allow_old_syntax:
                    raise TypeError(
                        f"The class {data_cls.__name__} is declaring entities using unsupported syntax in a\n"
                        f"superclass; entities in a superclass must be annotated with either "
                        f"`{recommended_annotation_prefix}.EntityType` or ,\n"
                        f"`Annotated[type, xi.EntityType]; entities {', '.join(entities_to_list_in_error)} cannot be\n"
                        f"annotated as `xi.EntityType` (where EntityType is one of: Param, Scalar, Index, Series,\n"
                        f"DataFrame)"
                    )

                raise TypeError(
                    f"The class {data_cls.__name__} is using an unsupported syntax for specifying entities.\n" +
                    EntitiesConfig.__get_update_entity_syntax_message(entities_to_list_in_error,
                                                                      recommended_annotation_prefix)
                )

        #
        EntitiesConfig.__check_no_entity_class_attributes(data_cls,
                                                          recommended_annotation_prefix=recommended_annotation_prefix)

        #
        return entities or old_syntax_entities

    def _init_entities(self, data_cls: Type, recommended_annotation_prefix='xi.types',
                       allow_old_syntax=True) -> Mapping[str, EntityBase]:
        """
        Initialize the list of entities in the class.

        Parameters
        ----------
        data_cls : Type
            The class that will contain the entities.

        recommended_annotation_prefix : str
            The prefix for the recommended annotation functions to use for generating annotations for this class,
            e.g. "xi.types".

        allow_old_syntax : bool
            If true, allow the 'old' syntax of using the EntityBase subclasses directly as type hints in the
            limited case where all the entities defined in the container use this syntax.
        """

        self.__entities = self.__get_entities(data_cls,
                                              recommended_annotation_prefix=recommended_annotation_prefix,
                                              allow_old_syntax=allow_old_syntax)
        self.__init_entity_names()
        data_cls._entities_cfg = self

        return MappingProxyType(self.__entities)

    @property
    def entities(self) -> ValuesView[EntityBase]:
        """
        Get the list of all Insight entities of an app or scenario data container.

        Returns
        -------
        entities : ValuesView[EntityBase]
            The Insight entities.

        See Also
        --------
        AppConfig.get_entity
        AppConfig
        EntityBase
        """
        return self.__entities.values()

    def get_entity(self, name: str) -> Optional[EntityBase]:
        """
        Get an Insight entity by name.

        Parameters
        ----------
        name : str
            The name of the attribute in which the entity is stored.
            Column entities can be requested using the syntax `"<frame_name>.<column_name>"`.

        Returns
        -------
        entity : Optional[EntityBase]
            The Insight entity or `None` if not found.

        See Also
        --------
        AppConfig.entities
        AppConfig
        EntityBase
        """
        entity = self.__entities.get(name)

        if entity is None and name.find('.') > 0:
            #
            (frame_name, column_name) = name.split('.', 1)
            frame = self.get_entity(frame_name)
            if frame is not None and isinstance(frame, DataFrameBase):
                entity = next((col for col in frame.columns if col.name == column_name), None)

        return entity

    def _get_entities_filter(self,
                             entities: Union[Iterable[EntityBase], Iterable[str]] = None,
                             *,
                             manage: Manage = None,
                             entity_filters: Iterable[Callable[[Entity], bool]] = None,
                             ) -> Callable[[Entity], bool]:
        """ Generate a filter function that accepts entities based on the given settings.

        entities : Union[Iterable[Entity], Iterable[str]], optional = None
            Either names of entities or entities themselves.
            When passing names, both entity name and attribute name will be checked (for column entities,
            the entity name and the qualified column name "<frame_name>.<column_name>").
            If the name of a data frame is included, all its columns will pass the filter.
            Errors will be raised if an entity name is unrecognized.
        manage: Manage, optional
            The manage-type of entities to pass.
        entity_filters: Iterable[Callable[[EntityBase], bool]], optional
            Function to filter available entities to decide if they are to be initialized.  If an entity filter is
            provided, this will be applied in addition to the entity names / manage / other filters.
        """

        #
        if entities is None:
            entities_to_accept = None
        elif all(isinstance(e, str) for e in entities):
            entities_to_accept = get_non_composed_entities_from_names(self.__entities.values(), entities)
        elif all(isinstance(e, EntityBase) for e in entities):
            entities_to_accept = get_non_composed_entities(entities)
        else:
            raise TypeError("entities argument must be an iterable of strings of an iterable of entities.")

        if entities_to_accept is None:
            entities_to_accept = set(get_non_composed_entities(self.entities))
        else:
            entities_to_accept = set(entities_to_accept)

        def accept_entity(entity: Entity) -> bool:
            if entity not in entities_to_accept:
                return False
            if manage and entity.manage != manage:
                return False
            if entity_filters and any(not fil(entity) for fil in entity_filters):
                return False
            return True

        return accept_entity

    def _get_entities(self,
                      entities: Union[Iterable[EntityBase], Iterable[str]] = None,
                      *,
                      manage: Manage = None,
                      entity_filters: Iterable[Callable[[Entity], bool]] = None,
                      ) -> Iterable[Entity]:
        """ Creates filter as described and applies it to the entities of this container.
            See _get_entities_filter for description of parameters. """
        complete_filter = self._get_entities_filter(
            entities=entities,
            manage=manage,
            entity_filters=entity_filters
        )
        return [e for e in get_non_composed_entities(self.__entities.values()) if complete_filter(e)]

    def _get_entity_names(self,
                          entities: Union[Iterable[EntityBase], Iterable[str]] = None,
                          *,
                          manage: Manage = None,
                          entity_filters: Iterable[Callable[[Entity], bool]] = None,
                          ) -> Iterable[str]:
        """ Creates filter as described and applies it to the entities of this container, returning the
            entity names.
            See _get_entities_filter for description of parameters. """
        return [e.entity_name for e in self._get_entities(entities=entities, manage=manage,
                                                          entity_filters=entity_filters)]


class EntitiesContainer:
    """
    Abstract base class used for classes that contain scenario entities (such as `AppBase` and
    `ScenarioData`), providing a standard way to query entity definitions.

    The `ScenarioData` decorator will automatically add the EntitiesContainer as a superclass of the class
    being defined, but it can also be added explicitly if required by static code analysis tools.

    Examples
    --------
    Example of decorating a class with ScenarioData and explicitly declaring the `EntitiesContainer` superclass:

    >>> @xi.ScenarioData
    ... class EntitiesToRead(xi.EntitiesContainer):
    ...     my_integer: xi.data.Scalar()
    ...     my_array: xi.data.Series()

    See Also
    --------
    ScenarioData
    """

    _entities_cfg: EntitiesConfig = None

    @classmethod
    def get_entities_cfg(cls) -> EntitiesConfig:
        """ Return the configuration for entities stored in this class. """
        if not hasattr(cls, "_entities_cfg") or not cls._entities_cfg:
            raise AttributeError(
                f"Cannot access the entities container configuration!\n"
                f"    Please make sure that the class \"{cls.__name__}\" is decorated with the AppConfig or "
                f"ScenarioData\n"
                f"    decorator.")
        return cls._entities_cfg

    @property
    def entities_cfg(self) -> EntitiesConfig:
        """
        Property for the entities configuration for entities stored in this class.

        Returns
        -------
        entities_cfg : EntitiesConfig
            The entities configuration object.

        Examples
        --------
        Demonstration of using the entities configuration for listing the entity names:

        >>> @xi.ScenarioData
        ... class EntitiesToRead(xi.EntitiesContainer):
        ...     my_integer: xi.data.Scalar()
        ...     my_array: xi.data.Series()
        ...
        ... data = EntitiesToRead()
        ... for e in data.entities_config.entities:
        ...    print(f'Found entity {e.name}')

        See Also
        --------
        AppBase.app_cfg
        """
        return self.__class__.get_entities_cfg()


class ScenarioData(EntitiesConfig):
    """
    Insight scenario data class decorator. A class used to receive data from another scenario or app must use this
    decorator.

    The `ScenarioData` decorator will automatically add `EntitiesContainer` as a superclass of the supplied class
    definition, if it is not already present.

    Examples
    --------
    Example of a decorating a class with ScenarioData:

    >>> @xi.ScenarioData
    ... class EntitiesToRead:
    ...     my_integer: xi.data.Scalar()
    ...     my_string: xi.data.Scalar()
    ...     my_set: xi.data.Index()
    ...     my_array: xi.data.Series()
    ...     my_table: xi.data.DataFrame(
    ...         columns=[
    ...             xi.data.Column('my_first_array'),
    ...             xi.data.Column('my_second_array')])
    ...
    ... SCENARIO_PATH = '/MyApp/MyFolder/MyScenario'
    ... my_data = self.insight.get_scenario_data(SCENARIO_PATH, EntitiesToRead)
    ... print(f"the integer scalar I read is {my_data.my_integer}")

    See Also
    --------
    ScenarioData.__init__
    AppInterface.get_scenario_data
    EntitiesContainer
    """

    # pylint will notify us this constructor is useless because it just delegates to the superclass.
    #
    # pylint: disable-next=useless-parent-delegation
    def __init__(self):
        """
        Insight scenario data class decorator. Use this decorator to decorate a class used to receive data from another
        scenario.

        See Also
        --------
        ScenarioData
        EntitiesContainer
        AppInterface.get_scenario_data
        """
        super().__init__()

    def __call__(self, data_container_class):
        #
        if issubclass(data_container_class, EntitiesContainer):
            entities_container_subclass = data_container_class
        else:
            entities_container_subclass = type(data_container_class.__name__,
                                               (data_container_class, EntitiesContainer), {})

        self._init_entities(entities_container_subclass, recommended_annotation_prefix="xi.data",
                            allow_old_syntax=False)

        for entity in self.entities:
            entity._check_valid_scenario_data_entity()

        return entities_container_subclass
