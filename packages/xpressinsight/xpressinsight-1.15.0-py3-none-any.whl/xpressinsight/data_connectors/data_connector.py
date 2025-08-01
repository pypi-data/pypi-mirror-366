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

from abc import ABC, abstractmethod
from typing import Callable, Dict, Type, Any

from .. import EntitiesContainer, entities as xi_entities
from ..entities import basic_types as xi_types

SingleValueDict = Dict[Type[xi_types.BasicType], Dict[str, Any]]


class DataConnector(ABC):
    """
    DataConnector manages interactions between an entity data container (e.g. an application instance) and
    some data store.
    """

    # noinspection PyUnusedLocal
    @abstractmethod
    def __init__(self, data_container: EntitiesContainer):
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """ Check if the data store is empty. """

    @abstractmethod
    def clean(self) -> None:
        """ Cleans the data store, removing any locally saved files. """

    @abstractmethod
    def initialize_entities(self, entity_filter: Callable[[xi_entities.Entity], bool], overwrite: bool = True) -> None:
        """ Initialize all entities matching the given filter to suitable default values.
            Raise an error if an entity already has a value and overwrite=False. """

    @abstractmethod
    def load_entities(self, entity_filter: Callable[[xi_entities.Entity], bool]) -> None:
        """ Load all entities matching the filter from the data-store. """

    @abstractmethod
    def save_entities(self, entity_filter: Callable[[xi_entities.Entity], bool]) -> None:
        """ Save all entities matching the filter to the data-store. """

    @abstractmethod
    def load_meta(self) -> SingleValueDict:
        """ Returns the meta-data from the data store. """
