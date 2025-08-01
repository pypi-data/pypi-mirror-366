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
import threading
from typing import ValuesView, Optional, Iterable, Callable, Union, Set

from .. import entities as xi_entities
from .data_connector import DataConnector
from ..entities import get_non_composed_entities, basic_types as xi_types
from ..slow_tasks_monitor import SlowTasksMonitor


class AppDataConnector:
    """
    AppDataConnector performs the requests to load / save the data for the application class as a whole.
    It does not subclass DataConnector, but rather wraps one and converts the higher-level requests made of the
    app (e.g. load input entities) to lower-level requests to the table connector (e.g. load these specific
    entities).
    """

    def __init__(self, app, base: DataConnector,
                 slow_tasks_monitor: Optional[SlowTasksMonitor] = None):
        self._app = app
        self._entities: ValuesView[xi_entities.EntityBase] = app.app_cfg.entities
        self._base = base
        self._lock = threading.RLock()  #
        self._result_entities_to_save: Optional[Set[xi_entities.Entity]] = None
        self._slow_tasks_monitor = slow_tasks_monitor or SlowTasksMonitor.default()

    def _load_meta(self):
        # pylint: disable=protected-access
        meta_values = self._base.load_meta()

        if 'http_port' in meta_values[xi_types.integer] and 'http_token' in meta_values[xi_types.string]:
            rest_port = meta_values[xi_types.integer]['http_port']
            rest_token = meta_values[xi_types.string]['http_token']
            # noinspection PyProtectedMember
            self._app.insight._init_rest(rest_port, rest_token)

        if 'app_id' in meta_values[xi_types.string]:
            self._app.insight._app_id = meta_values[xi_types.string]['app_id']

        if 'app_name' in meta_values[xi_types.string]:
            self._app.insight._app_name = meta_values[xi_types.string]['app_name']

        if 'scenario_id' in meta_values[xi_types.string]:
            self._app.insight._scenario_id = meta_values[xi_types.string]['scenario_id']

        if 'scenario_name' in meta_values[xi_types.string]:
            self._app.insight._scenario_name = meta_values[xi_types.string]['scenario_name']

        if 'scenario_path' in meta_values[xi_types.string]:
            self._app.insight._scenario_path = meta_values[xi_types.string]['scenario_path']

    def _warn_about_work_dir(self):
        if os.path.isdir(self._app.insight.work_dir):
            print("Test mode: Using existing Insight working directory.")

    def _check_base_exists(self):
        if self._base.is_empty():
            raise FileNotFoundError(f'Cannot find data store: "{self._base}".')

    def set_result_entities_to_save(self, entities: Iterable[xi_entities.Entity]) -> None:
        """
        Restrict the data-connector to be able to only capture the given entities in the results.
        """
        self._result_entities_to_save = set(entities)

    def reset_result_entities_to_save(self) -> None:
        """
        Reset the restriction on the entities to capture in the results.
        """
        self._result_entities_to_save = None

    def initialize_entities(self, *,
                            entities: Union[Iterable[str], Iterable[xi_entities.EntityBase]] = None,
                            manage: xi_entities.Manage = None,
                            entity_filter: Callable[[xi_entities.Entity], bool] = None,
                            overwrite: bool = False):
        """ Initialize entities to their default values.  Entities are filtered by the `names`, `entities`, `manage`
            and `entity_filter` arguments, or all entities will be initialized if none of these are set.

        Parameters
        ----------
        entities: Iterable[EntityBase], optional
            The entities or names of entities to be initialized. If a DataFrame object is included, all of its columns
            will be initialized.  Columns can be specified with their qualified names within the frame
            (ie "<frame_name>.<col_name>") as well as their entity names.
        manage: Manage, optional
            The manage-type of entities to be initialized.  Applied as an additional filter to the `names`/`entities`
            values (for example, to allow initialization of only RESULT columns of a DataFrame).
        entity_filter: Callable[[Entity], bool], optional
            Function to filter available entities to decide if they are to be initialized.
        overwrite: bool = False
            Flag indicating whether we should overwrite existing values.
            If not set to `True` and one of the selected entities has a value, a `ValueError` will be raised.
        """
        complete_filter = self._app.app_cfg._get_entities_filter(
            entities=entities,
            manage=manage,
            entity_filters=[entity_filter] if entity_filter else None
        )
        with self._lock:
            self._base.initialize_entities(entity_filter=complete_filter, overwrite=overwrite)

    def clear_input(self):
        """ Clear values of input entities, setting parameters/scalars to default values. """
        with self._lock:
            if self._app.insight.test_mode:
                self._warn_about_work_dir()
                is_empty_data_repo = self._base.is_empty()

                if is_empty_data_repo:
                    print(f'Test mode: Creating new data repository in: "{self._app.insight.work_dir}".\n'
                          'Test mode: Setting uninitialized parameters and scalars to default value.\n')

                else:
                    print(f'Test mode: Loading parameters from data repository in: "{self._app.insight.work_dir}".\n'
                          'Test mode: Setting uninitialized scalars to default value.\n')
                    #
                    self._load_meta()
                    #
                    self._base.load_entities(lambda entity: isinstance(entity, xi_entities.Param))

                #
                self._base.initialize_entities(lambda entity: (isinstance(entity, xi_entities.Param) and
                                                               entity.name not in self._app.__dict__))

                #
                self._base.initialize_entities(lambda entity: (isinstance(entity, xi_entities.Scalar) and
                                                               (entity.manage == xi_entities.Manage.RESULT or
                                                                entity.name not in self._app.__dict__)))

                #
                self._base.clean()

                #
                self._base.save_entities(lambda entity: isinstance(entity, xi_entities.Param))

            else:
                self._check_base_exists()

                #
                self._load_meta()
                #
                self._base.load_entities(lambda entity: isinstance(entity, xi_entities.Param))
                #
                self._base.initialize_entities(lambda entity: (isinstance(entity, xi_entities.Scalar) and
                                                               (entity.is_managed == xi_entities.Manage.RESULT or
                                                                entity.name not in self._app.__dict__)))

    def save_input(self):
        """ Save values of input entities. """
        with self._lock:
            self._base.save_entities(lambda entity: entity.is_managed(xi_entities.Manage.INPUT))

    def load_input(self):
        """ Load values of input entities. """
        with self._lock:
            if self._app.insight.test_mode:
                self._warn_about_work_dir()
                if self._base.is_empty():
                    print(f'Test mode: Creating new data repository: "{self._app.insight.work_dir}".\n'
                          'Test mode: Setting uninitialized parameters and scalars to default value.\n'
                          'Test mode: Inputs have to be initialized manually before calling this execution mode.\n')
                    self._base.clean()
                    self._base.initialize_entities(lambda entity: (isinstance(entity, xi_entities.ScalarBase) and
                                                                   entity.is_managed(xi_entities.Manage.INPUT) and
                                                                   entity.name not in self._app.__dict__))
                    self.save_input()

                else:
                    print(f'Test mode: Loading parameters and input from data '
                          f'repository: "{self._app.insight.work_dir}".\n')
                    self._load_meta()

                    self._base.load_entities(lambda entity: entity.is_managed(xi_entities.Manage.INPUT))

            else:
                self._check_base_exists()
                self._load_meta()
                self._base.load_entities(lambda entity: entity.is_managed(xi_entities.Manage.INPUT))

            #
            self._base.initialize_entities(lambda entity: (isinstance(entity, xi_entities.Scalar) and
                                                           entity.manage == xi_entities.Manage.RESULT))

    def load_params(self):
        """ Load values of parameter entities only. """
        with self._lock:
            if self._app.insight.test_mode:
                self._warn_about_work_dir()
                if self._base.is_empty():
                    print(f'Test mode: Creating new data repository: "{self._app.insight.work_dir}".\n'
                          'Test mode: Setting uninitialized parameters to default value.\n'
                          'Test mode: Inputs have to be initialized manually before calling this execution mode.\n')
                    self._base.clean()
                    self._base.initialize_entities(lambda entity: (isinstance(entity, xi_entities.ScalarBase) and
                                                                   entity.is_managed(xi_entities.Manage.INPUT) and
                                                                   entity.name not in self._app.__dict__))
                    self.save_input()

                else:
                    print(f'Test mode: Loading parameters from data '
                          f'repository: "{self._app.insight.work_dir}".\n')
                    self._load_meta()
                    self._base.load_entities(lambda entity: isinstance(entity, xi_entities.Param))

            else:
                self._check_base_exists()
                self._load_meta()
                self._base.load_entities(lambda entity: isinstance(entity, xi_entities.Param))

            #
            self._base.initialize_entities(lambda entity: isinstance(entity, xi_entities.Scalar))

    def load_partial_input(self, entities: Iterable[xi_entities.Entity]):
        """ Load values of a subset of the input entities. Non-input or otherwise invalid entities in the
            supplied list will be ignored. """
        entities = set(entities)

        #
        #
        assert self._app.insight.test_mode

        with self._lock:
            #
            #
            for entity in entities:
                if isinstance(entity, xi_entities.Column):
                    df = entity._data_frame
                    if df.name in self._app.__dict__:
                        del self._app.__dict__[df.name]

            self._warn_about_work_dir()
            if self._base.is_empty():
                print(f'Test mode: Creating new data repository: "{self._app.insight.work_dir}".\n'
                      'Test mode: Setting uninitialized scalars to default value.\n'
                      'Test mode: Inputs have to be initialized manually before calling this execution mode.\n')
                self._base.clean()
                #
                #
                #
                self._base.initialize_entities(lambda entity: (isinstance(entity, xi_entities.Scalar) and
                                                               entity.is_managed(xi_entities.Manage.INPUT) and
                                                               entity.name not in self._app.__dict__))
                self.save_input()

            else:
                print(f'Test mode: input from data repository: "{self._app.insight.work_dir}".\n')
                self._load_meta()

                self._base.load_entities(lambda entity: (entity.is_managed(xi_entities.Manage.INPUT)
                                                         and entity in entities))

    def save_result(self):
        """ Save values of result and update-after-execution entities. """
        with self._lock:
            if self._app.insight.test_mode:
                if self._result_entities_to_save is not None:
                    entities_to_save = self._result_entities_to_save
                else:
                    entities_to_save = set(e for e in get_non_composed_entities(self._app.app_cfg.entities)
                                           if e.is_managed(xi_entities.Manage.RESULT))

                #
                self._base.save_entities(lambda entity: (entity in entities_to_save))


            else:
                #
                #
                self._base.save_entities(lambda e: ((e in self._result_entities_to_save)
                                                    if self._result_entities_to_save
                                                    else e.is_managed(xi_entities.Manage.RESULT)))

    def save_progress(self):
        """ Save values of progress entities. """
        with self._lock:
            self._base.save_entities(lambda entity: entity.update_progress)

    @property
    def base(self):
        """ Generic DataContainer being used by the app. """
        return self._base
