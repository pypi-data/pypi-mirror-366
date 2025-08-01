"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Implement various entity-related utility functions.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from typing import Iterable

from .data_frame import DataFrameBase
from .entity import Entity, EntityBase


def get_non_composed_entities(entities: Iterable[EntityBase]) -> Iterable[Entity]:
    """ Given a sequence of entities, return the non-composed entities contained within.
        Ie if the entities list contains an entity E, the result will contain the columns of E if E is a DataFrame,
        or E if it is not.
    """
    non_composed_entities = []
    for entity in entities:
        if isinstance(entity, DataFrameBase):
            non_composed_entities.extend(entity.columns)
        else:
            non_composed_entities.append(entity)
    return non_composed_entities


def get_non_composed_entities_from_names(entities: Iterable[EntityBase], names: Iterable[str]) -> Iterable[Entity]:
    """ Find entity objects for the given names from the given entities. Only non-composed entities will be returned
        (ie no DataFrames). For each name, entities will be chosen as follows:
        If name matches name attribute of a non-DataFrame entity, return this.
        If name matches a DataFrame entity, return all Columns in that entity.
        If name matches entity name of a Column entity, return that column.
        If name matches pattern <frame-name>.<column-name>, return that Column entity.
        If name does not match any entity, raise a ValueError.
    """
    #
    #
    names_remaining = set(names)

    #
    selected_entities = []
    for entity in entities:
        #
        if entity.name in names_remaining:
            names_remaining.remove(entity.name)

            #
            if isinstance(entity, DataFrameBase):
                selected_entities.extend(entity.columns)
            else:
                selected_entities.append(entity)

        elif isinstance(entity, DataFrameBase):
            #
            for col in entity.columns:
                if col.entity_name in names_remaining:
                    names_remaining.remove(col.entity_name)
                    selected_entities.append(col)
                elif f"{entity.name}.{col.name}" in names_remaining:
                    names_remaining.remove(f"{entity.name}.{col.name}")
                    selected_entities.append(col)

    #
    if names_remaining:
        raise ValueError(f'The following {"entities were" if len(names_remaining)>1 else "entity was"} not found: ' +
                         ', '.join([f'"{n}"' for n in sorted(names_remaining)]))

    return selected_entities
