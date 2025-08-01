"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly. This defines functions and classes for accessing Insight
    scenario entity data through the REST interface.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
# pylint: disable=protected-access,too-many-instance-attributes,too-many-arguments,too-few-public-methods

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Union, Iterable, Tuple, Dict, List, TypeVar, Type

import pandas as pd

from . import models
from .rest_client_base import InsightRestClientBase
from .. import polars_shims as pl
from .. import data_connectors
from .. import entities as xi_entities
from ..entities_config import EntitiesContainer


@dataclass
class EntityUpdate(ABC):
    """
    Abstract superclass representing an update to be applied to the value of an entity in a scenario.

    Attributes
    ----------
    entity_name : str
        The name of the entity being updated.

    See Also
    --------
    scenario.ArrayUpdate
    scenario.IndexUpdate
    scenario.ScalarUpdate
    scenario.InsightRestClient.update_scenario_data
    """
    entity_name: str

    @abstractmethod
    def _to_rest_api_model(self) -> models.EntityDelta:
        """ Convert this update into a format suitable for sending to the Insight REST API. """


@dataclass
class ScalarUpdate(EntityUpdate):
    """
    Representation of an update to be applied to the value of a scalar entity.

    Attributes
    ----------
    entity_name : str
        The name of the entity being updated.
    value : Union[str, int, float, bool]
        The new value for the scalar. Must match the type of the entity in the target scenario.

    Examples
    --------
    Update the value of the entity `MAX_HOURS_PER_WEEK` in the scenario `570b9100-46e3-4643-baee-2e24aa538f25`
    to 40.5.

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
    ...         ScalarUpdate('MAX_HOURS_PER_WEEK', 40.5)])

    See Also
    --------
    scenario.InsightRestClient.update_scenario_data
    """
    value: Union[str, int, float, bool]

    def _to_rest_api_model(self) -> models.EntityDelta:
        if not isinstance(self.value, (str, int, float, bool)):
            raise TypeError(f'Scalar "{self.entity_name}" delta has value of unsupported '
                            f'type "{type(self.value).__name__}"')
        return models.EntityDelta(entity_name=self.entity_name, value=self.value)


#
SET_ELEM = Union[str, int, bool]
SET_ELEMS_ITERABLE = Union[Iterable[str], Iterable[int], Iterable[bool]]
SET_ELEMS_LIST = Union[List[str], List[int], List[bool]]


@dataclass
class IndexUpdate(EntityUpdate):
    """
    Representation of an update to the value of an index entity (also known as a set entity).

    Attributes
    ----------
    entity_name : str
        The name of the entity being updated.
    add : Union[Iterable, pd.Series, pd.Index, pl.Series], optional
        A list of values to add to the set. Can be a Pandas index or series, a Polars series, or any Iterable.
        If a Pandas series, the index of the series is ignored.
        If a Pandas index, must not be a multi-index.
    remove : Union[Iterable, pd.Series, pd.Index, pl.Series], optional
        A list of values to remove from the set. Can be a Pandas index or series, a Polars series, or any Iterable.
        If a Pandas series, the index of the series is ignored.
        If a Pandas index, must not be a multi-index.

    Examples
    --------
    Add the values `Saturday` and `Sunday` to the index DAYS, and remove `Wednesday` and `Thursday`:

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
    ...         IndexUpdate('DAYS', add=['Saturday', 'Sunday'],
    ...                             remove=['Wednesday', 'Thursday'])])

    Add the values `Saturday` and `Sunday` to the index DAYS, and remove `Wednesday` and `Thursday`, using Pandas
    data types:

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
    ...         IndexUpdate('DAYS', add=pd.Series(['Saturday', 'Sunday']),
    ...                             remove=pd.Index(['Wednesday', 'Thursday']))])

    Add the values `Saturday` and `Sunday` to the index DAYS, using Polars data types:

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
    ...         IndexUpdate('DAYS', add=pl.Series(['Saturday', 'Sunday']))])

    Notes
    -----
    Whichever data type is used when passing the 'add' and 'remove' lists, it must contain values of the
    required type for this set entity.

    See Also
    --------
    scenario.InsightRestClient.update_scenario_data
    """
    add: Optional[Union[SET_ELEMS_ITERABLE, pd.Series, pd.Index, pl.Series]] = None
    remove: Optional[Union[SET_ELEMS_ITERABLE, pd.Series, pd.Index, pl.Series]] = None

    def _to_rest_api_model(self) -> models.EntityDelta:
        return models.EntityDelta(entity_name=self.entity_name, set_delta=models.SetDelta(
            add=self._to_validated_list_of_set_elements(self.add),
            remove=self._to_validated_list_of_set_elements(self.remove),
        ))

    def _to_validated_list_of_set_elements(self,
                                           values: Optional[Union[SET_ELEMS_ITERABLE, pd.Series, pd.Index, pl.Series]]
                                           ) -> Optional[SET_ELEMS_LIST]:
        """ Convert the many ways we can supply a list of set values into a suitable Iterable. validating the
            values as we go. """
        lst = self._to_list_of_set_elements(values)
        self._validate_list_of_set_elements(lst)
        return lst

    def _to_list_of_set_elements(self, values: Optional[Union[SET_ELEMS_ITERABLE, pd.Series, pd.Index, pl.Series]]) -> (
            Optional[SET_ELEMS_LIST]):
        """ Convert the many ways we can supply an iterable of set values into a suitable List. """
        if values is None:
            return None

        if isinstance(values, (pl.Series, pd.Series)):
            values = values.to_list()

        elif isinstance(values, pd.Index):
            if isinstance(values, pd.MultiIndex):
                raise TypeError(f'Set "{self.entity_name}" delta must not be a multi-index')
            values = values.to_list()

        elif not isinstance(values, Iterable):
            raise TypeError(f'Set "{self.entity_name}" delta must be either Iterable, Pandas Series, Pandas Index or '
                            f'Polars Series, but found "{type(values).__name__}"')

        elif not isinstance(values, list):
            values = list(values)

        if len(values) == 0:
            return None

        return values

    def _validate_list_of_set_elements(self, values: Optional[SET_ELEMS_LIST]) -> None:
        """ Validate that the members of the given list of values are of supported and consistent types.  """
        if values is None or len(values) == 0:
            return

        #
        if isinstance(values[0], str):
            expected_type = str
        elif isinstance(values[0], int):
            expected_type = int
        elif isinstance(values[0], bool):
            expected_type = bool
        else:
            raise TypeError(f'Elements in set "{self.entity_name}" delta must be either str, int or bool, but '
                            f'found "{type(values[0]).__name__}"')

        #
        if not all(isinstance(x, expected_type) for x in values):
            types_found = {type(x) for x in values}
            #
            raise TypeError(f'Expected elements in set "{self.entity_name}" delta to have same type '
                            f'"{expected_type.__name__}", but found types: {sorted([t.__name__ for t in types_found])}')


#
ARRAY_ELEM_VALUE = Union[int, str, float, bool]
ARRAY_INDEX_TUPLE = Union[Tuple[SET_ELEM, ...], SET_ELEM]
ARRAY_INDEX_TUPLES = Union[Iterable[Tuple[SET_ELEM, ...]], SET_ELEMS_ITERABLE]
ARRAY_AS_DICT = Dict[Union[Tuple[SET_ELEM, ...], SET_ELEM], ARRAY_ELEM_VALUE]


@dataclass
class ArrayUpdate(EntityUpdate):
    """
    Representation of an update to the applied to the value of an array entity.

    Attributes
    ----------
    entity_name : str
        The name of the entity being updated.
    add : Union[Dict, pd.Series, pl.DataFrame], optional
        The list of values to add or update in the array. May be a Dictionary, a Pandas Series or a Polars DataFrame.
        If a Polars DataFrame, it's assumed the rightmost column is the value, and the other columns are the
        index values, in the same order as specified in the Insight schema.
        If a Dictionary, the keys may be single values (for a single-index array), or tuples (for a multi-index array).
    remove : Union[Iterable, pd.Index, pl.DataFrame], optional
        A list of index entries to remove from the array. May be an Iterable, a Pandas Index or a Polars DataFrame.
        If a Pandas Index, it should be a MultiIndex if the array has multiple indexes.
        If a Polars DataFrame, it's assumed that each column represents one of the index entities, in the same
        other as specified in the Insight schema.
        Otherwise, it should be an iterable containing either the index values to remove (for a single-index array),
        or tuples (for a multi-index array).

    Examples
    --------
    Add or update values in the single-index array 'DAY_NAMES':

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     entries_to_add = {6: 'Saturday', 7: 'Sunday'}
    ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
    ...         ArrayUpdate('DAY_NAMES', add=entries_to_add)])

    Add or update values in the multi-index array 'SALES':

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     entries_to_add = {('Washington', 'January'): 25.1,
    ...                       ('Washington', 'February'): 30.7,
    ...                       ('Delaware', 'January'): 2.0}
    ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
    ...         ArrayUpdate('SALES', add=entries_to_add)])

    Add or update values in the multi-index array 'SALES', using a Pandas series:

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     entries_to_add = pd.Series([25.1, 30.7, 2.0],
    ...         index=pd.MultiIndex.from_tuples([('Washington', 'January'),
    ...                                          ('Washington', 'February'),
    ...                                          ('Delaware', 'January')])
    ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
    ...         ArrayUpdate('SALES', add=entries_to_add)])

    Add or update values in the multi-index array 'SALES', using a Polars data-frame:

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     entries_to_add = pl.DataFrame({
    ...         'Location': ['Washington', 'Washington', 'Delaware'],
    ...         'Month': ['January', 'February', 'January'],
    ...         'Value': [25.1, 30.7, 2.0]})
    ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
    ...         ArrayUpdate('SALES', add=entries_to_add)])

    Remove values from the single-index array 'DAY_NAMES':

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
    ...         ArrayUpdate('DAY_NAMES', remove=[6, 7])])

    Remove values in the multi-index array 'SALES':

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
    ...         ArrayUpdate('SALES', remove=[('Toronto', 'January'),
    ...                                      ('Toronto', 'February'),
    ...                                      ('Toronto', 'March')])])

    Remove values in the multi-index array 'SALES', using Pandas data-types:

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     entries_to_remove = pd.MultiIndex.from_product([['Toronto'],
    ...             ['January', 'February', 'March']])
    ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
    ...         ArrayUpdate('SALES', remove=entries_to_remove)])

    Remove values in the multi-index array 'SALES', using Polars data-types:

    >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
    ...     entries_to_remove = pl.DataFrame({
    ...         'Location': ['Toronto', 'Toronto', 'Toronto'],
    ...         'Month': ['January', 'February', 'March']})
    ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
    ...         ArrayUpdate('SALES', remove=entries_to_remove)])

    Notes
    -----
    Whichever data type is used when passing the 'add' and 'remove' arguments, it must contain values of the
    required types for the value and indexes of this array entity.

    See Also
    --------
    scenario.InsightRestClient.update_scenario_data
    """
    add: Optional[Union[ARRAY_AS_DICT, pd.Series, pl.DataFrame]] = None
    remove: Optional[Union[ARRAY_INDEX_TUPLES, pd.Index, pl.DataFrame]] = None

    def _to_rest_api_model(self) -> models.EntityDelta:
        return models.EntityDelta(entity_name=self.entity_name, array_delta=models.ArrayDelta(
            add=self._to_validated_list_of_array_elements(self.add),
            remove=self._to_validated_list_of_index_tuples(self.remove),
        ))

    def _to_validated_list_of_array_elements(self, values: Optional[Union[ARRAY_AS_DICT, pd.Series, pl.DataFrame]]
                                             ) -> Optional[List[models.ArrayElement]]:
        """ Convert the many ways we can supply the array elements to set into a list of models.ArrayElement, performing
            validation that the given index and value types are supported and consistent. """
        #
        #
        #
        #
        elems = self._to_list_of_array_element_tuples(values)
        self._validate_list_of_array_element_tuples(elems)

        #
        return (None if elems is None else
                [models.ArrayElement(key=elem[0], value=elem[1]) for elem in elems])

    def _to_list_of_array_element_tuples(self, values: Optional[Union[ARRAY_AS_DICT, pd.Series, pl.DataFrame]]) -> (
            Optional[List[Tuple[Tuple[SET_ELEM, ...], ARRAY_ELEM_VALUE]]]):
        """ Convert the many ways we can supply the array elements to set into a list of tuples"""
        if values is None:
            return None

        #
        if isinstance(values, pd.Series):
            elems = [((key if isinstance(key, tuple) else (key,)), value) for (key, value) in values.items()]

        elif isinstance(values, pl.DataFrame):
            if values.width < 2:
                raise TypeError(f'Array "{self.entity_name}" delta passed a Polars DataFrame with less than 2 columns')
            elems = [(row[:-1], row[-1]) for row in values.iter_rows() if row[:-1] is not None]

        elif not isinstance(values, Dict):
            raise TypeError(f'Array "{self.entity_name}" delta must be either Dictionary, Pandas Series, or Polars '
                            f'DataFrame, but found "{type(values).__name__}"')

        else:
            elems = [((k if isinstance(k, tuple) else (k,)), v) for (k, v) in values.items() if v is not None]

        #
        if len(elems) == 0:
            return None

        return elems

    def _validate_list_of_array_element_tuples(self,
                                               elems: Optional[List[Tuple[Tuple[SET_ELEM, ...], ARRAY_ELEM_VALUE]]]
                                              ) -> None:
        """ Given a list of array elements as tuples, validate their types are supported and consistent. """
        if elems is None or len(elems) == 0:
            return

        #
        first_elem = elems[0]
        if any(not isinstance(x, (str, int, bool)) for x in first_elem[0]):
            raise TypeError(f'Array "{self.entity_name}" index values must be of type str, int, or bool, but '
                            f'found {[type(x).__name__ for x in first_elem[0]]}')
        if not isinstance(first_elem[1], (str, int, bool, float)):
            raise TypeError(f'Array "{self.entity_name}" values must be of type str, int, float, or bool, but '
                            f'found "{type(first_elem[1]).__name__}"')

        #
        for elem in elems:
            if len(elem[0]) != len(first_elem[0]):
                raise ValueError(f'Array "{self.entity_name}" index tuples must be of same length')

            if any(not isinstance(i1, type(i2)) for (i1, i2) in zip(elem[0], first_elem[0])):
                raise TypeError(f'Array "{self.entity_name}" index tuples must be of same types, but '
                                f'found a tuple with types {[type(i).__name__ for i in first_elem[0]]} and another '
                                f'with types {[type(i).__name__ for i in elem[0]]}')
            if not isinstance(first_elem[1], type(elem[1])):
                raise TypeError(f'Array "{self.entity_name}" values must be of same type, but '
                                f'found one value with type "{type(first_elem[1]).__name__}" and another with '
                                f'type "{type(elem[1]).__name__}"')

    def _to_validated_list_of_index_tuples(self, values: Optional[Union[ARRAY_INDEX_TUPLES, pd.Index, pl.DataFrame]]
                                           ) -> Optional[List[Tuple[SET_ELEM, ...]]]:
        """ Convert the many ways we can supply the array keys to remove into a list of tuple values, validating
            the supplied values. """
        tuples = self._to_list_of_index_tuples(values)
        self._validate_list_of_index_tuples(tuples)
        return tuples

    def _to_list_of_index_tuples(self, values: Optional[Union[ARRAY_INDEX_TUPLES, pd.Index, pl.DataFrame]]) -> (
            Optional[List[Tuple[SET_ELEM, ...]]]):
        """ Convert the many ways we can supply the array keys to remove into a list of tuple values """
        if values is None:
            return None

        if isinstance(values, pd.MultiIndex):
            tuples = values.to_list()

        elif isinstance(values, pd.Index):
            tuples = [(v,) for v in values.to_list()]

        elif isinstance(values, pl.DataFrame):
            tuples = values.rows()

        elif not isinstance(values, Iterable):
            raise TypeError(f'Array "{self.entity_name}" removal delta must be either Iterable, Pandas Index, or '
                            f'Polars DataFrame, but found "{type(values).__name__}"')

        else:
            tuples = [(v if isinstance(v, tuple) else (v,)) for v in values]

        #
        if len(tuples) == 0:
            return None

        return tuples

    def _validate_list_of_index_tuples(self, tuples: Optional[List[Tuple[SET_ELEM, ...]]]) -> None:
        """ Given list of index tuples, validate they're all the same size and contain values of the same
            types in the same positions. """
        if tuples is None or len(tuples) == 0:
            return

        #
        first_tuple = tuples[0]
        if any(not isinstance(x, (str, int, bool)) for x in first_tuple):
            raise TypeError(f'Array "{self.entity_name}" index values must be of type str, int, or bool, but '
                            f'found {[type(x).__name__ for x in first_tuple]}')

        #
        for t in tuples:
            if len(t) != len(first_tuple):
                raise ValueError(f'Array "{self.entity_name}" index tuples must be of same size')

            if any(not isinstance(i1, type(i2)) for (i1, i2) in zip(t, first_tuple)):
                raise TypeError(f'Array "{self.entity_name}" index tuples must be of the same types, but '
                                f'found a tuple with types {[type(i).__name__ for i in first_tuple]} and another with '
                                f'types {[type(i).__name__ for i in t]}')


#
#
#
#
SCENARIO_DATA_CONTAINER = TypeVar('SCENARIO_DATA_CONTAINER')


# noinspection PyProtectedMember
class InsightScenarioDataOperations(InsightRestClientBase, ABC):
    """
    Implementation of calls to scenario-entity-data-related endpoints in the Insight REST API.
    """

    @staticmethod
    def _get_array_filters(filters: Optional[Dict[str, Dict[str, Iterable]]]) -> List[models.ArrayFilter]:
        #
        if filters is None:
            return []

        return [models.ArrayFilter(
            entity_name=entity_name,
            filter_id=f'filter_{filter_count}',
            index_filters={name: list(values) for (name, values) in index_filters.items()}
        ) for (filter_count, (entity_name, index_filters)) in enumerate(filters.items(), start=1)]

    def get_scenario_data(self, scenario_id: str, scenario_data_class: Type[SCENARIO_DATA_CONTAINER],
                          filters: Optional[Dict[str, Dict[str, Iterable]]] = None) -> SCENARIO_DATA_CONTAINER:
        """
        Loads the entities described in annotations on the given class, from the given scenario, into an instance
        of the given class.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario from which to read.
        scenario_data_class : Type[EntityContainer]
            A class declared with the `ScenarioData` or `AppConfig` decorator, describing entities to capture
            with class attributes with `xi.data.` or `xi.types.` type hints.
        filters : Dict[str, Dict[str, Iterable]], optional
            A dictionary of filters to apply when reading each array. The key of the dictionary is the entity name
            of the array (which may be different from  the attribute name or the column name in the
            `scenario_data_class`), and the value is a dictionary from index set entity name to the allowed
            values for those sets.

        Returns
        -------
        scenario_data : SCENARIO_DATA_CLASS
            An instance of the supplied `scenario_data_class`, populated with values read from the scenario.

        Raises
        ------
        scenario.ItemNotFoundError
            If there is no scenario with this ID, or the REST API client credentials do not have permission to access
            it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server.

        Notes
        -----
        `scenario_data_class` must be a class that has type attributes annotated using the xpressinsight.data. or
        xpressinsight.types. helper functions, and it must be decorated using the ScenarioData or AppConfig decorator.
        It's recommended to use ScenarioData unless the class is the application class for the app being read from,
        as AppConfig will perform additional validation that is only relevent for application definitions.

        The caller may optionally restrict which rows of a `Series`, `DataFrame`, or `PolarsDataFrame` entity are
        returned by passing a dictionary of `filters`.  When an array is filtered, it's passed a dictionary
        from index entity name to the allowed values of that index set.  If an index set is not included in the
        filter, this is equivalent to allowing all set elements of that index set.

        This function requests data in JSON format using the Insight REST API. When requesting a nontrivial amount of
        data within an executing Insight app, it is more efficient to use :fct-ref:`AppInterface.get_scenario_data`,
        which transfers data using a compressed Parquet format.

        Examples
        --------
        Example of reading multiple entities from a scenario:

        >>> @xi.ScenarioData()
        ... class EntitiesToRead:
        ...     my_integer: xi.data.Scalar(dtype=xi.integer)
        ...     my_string: xi.data.Scalar()
        ...     my_set: xi.data.Index()
        ...     my_array: xi.data.Series()
        ...     my_table: xi.data.DataFrame(
        ...         columns=[
        ...             xi.data.Column('my_first_column', dtype=xi.real),
        ...             xi.data.Column('my_second_column')])
        ...
        ... with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     SCENARIO_ID = '570b9100-46e3-4643-baee-2e24aa538f25'
        ...     scenario_data = client.get_scenario_data(SCENARIO_ID, SCENARIO_ID)
        ...     print(f'my_integer={scenario_data.my_integer}')

        Example of applying a filter to array being read:

        >>> @xi.ScenarioData()
        ... class EntitiesToRead:
        ...     factories: xi.data.DataFrame(
        ...         columns=[
        ...             xi.data.Column('sales'),
        ...             xi.data.Column('expenses')])
        ...
        ... # Fetch data for factories in Washington for the first 3 months of the year
        ... with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     # Apply a filter to both columns of the data-frame
        ...     factories_filter = {
        ...         'month': ['january', 'february', 'march'],
        ...         'state': ['Washington']
        ...     }
        ...     SCENARIO_ID = '570b9100-46e3-4643-baee-2e24aa538f25'
        ...     scenario_data = client.get_scenario_data(SCENARIO_ID, EntitiesToRead,
        ...         filters={'factories_sales': factories_filter,
        ...                  'factories_expenses': factories_filter})
        ...     print(scenario_data.factories)

        See Also
        --------
        AppInterface.get_scenario_data
        """
        if not issubclass(scenario_data_class, EntitiesContainer):
            #
            #
            raise TypeError("Scenario data class must be decorated with ScenarioData or AppConfig.")

        #
        scenario = self._make_json_request(
            method='GET',
            path=['api', 'scenarios', scenario_id],
            response_type=models.Scenario)

        #
        schema = self._make_json_request(
            method='GET',
            path=['api', 'apps', scenario.app.id, 'model-schema'],
            response_type=models.ModelSchema)

        #
        entity_names = list(scenario_data_class.get_entities_cfg()._get_entity_names(
            entity_filters=[lambda e: not isinstance(e, xi_entities.Param)]))
        filters = InsightScenarioDataOperations._get_array_filters(filters)
        param_names = list(scenario_data_class.get_entities_cfg()._get_entity_names(
            entity_filters=[lambda e: isinstance(e, xi_entities.Param)]))
        if param_names:
            #
            entity_names.append('parameters')
            filters.append(models.ArrayFilter(entity_name='parameters',
                                              index_filters={'parameter-names': param_names},
                                              filter_id='filter_parameters'))
        scenario_data_request = models.ScenarioDataQuery(entity_names=entity_names, filters=filters)

        #
        scenario_data = self._make_json_request(
            method='POST',
            path=['api', 'scenarios', scenario_id, 'data'],
            request_body=scenario_data_request,
            response_type=models.ScenarioData
        )

        container = scenario_data_class()
        connector = data_connectors.RestApiConnector(container, scenario_data, schema)
        with connector._connect():
            connector.load_entities(lambda e: True)

        return container

    def update_scenario_data(self, scenario_id: str, updates: Iterable[EntityUpdate], force_load: bool = False):
        """
        Update the values of one or more entities in an Insight scenario.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario to update.
        updates : Iterable[EntityUpdate]
            An iterable containing objects describing the changes to make to each entity.
        force_load : bool, default False
            If true, the scenario state will be set to 'loaded' if it's currently unloaded.

        Raises
        ------
        scenario.ItemNotFoundError
            If the scenario does not exist, or the REST API client credentials do not have permission to access it.
        scenario.InsightServerError
            If there is an issue communicating with the Insight server, or the supplied updates do not match.

        Examples
        --------
        Add 3 values to the array `NumberLabels` and update the value of the scalar `Status`:

        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.update_scenario_data('570b9100-46e3-4643-baee-2e24aa538f25', [
        ...         ArrayUpdate('NumberLabels',
        ...                     add=pd.Series(['One', 'Two', 'Three'],
        ...                                   index=pd.Index([1, 2, 3]))),
        ...         ScalarUpdate('Status', 'INITIALIZED')])

        More examples can be found in the documentation for :fct-ref:`ArrayUpdate`, :fct-ref:`ScalarUpdate`, and
        :fct-ref:`IndexUpdate`.

        Notes
        -----
        For indexes and arrays, scenario data updates are expressed as the changes to apply to the existing values.

        The REST API client credentials must authorise a user with write access to the scenario and the `SCENARIO_EDIT`
        authority.

        See Also
        --------
        scenario.ArrayUpdate
        scenario.IndexUpdate
        scenario.ScalarUpdate
        """
        self._make_json_request(
            method='PATCH',
            path=['api', 'scenarios', scenario_id, 'data'],
            request_body=models.ScenarioDataModification(
                deltas=[upd._to_rest_api_model() for upd in updates],
                force_load=force_load
            ),
            response_type=None,
            expected_status_code=204
        )
