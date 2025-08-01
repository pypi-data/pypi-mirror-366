"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import
    it directly. This defines functions and classes for executing Insight
    scenarios through the Insight REST interface.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
# pylint: disable=protected-access

from abc import ABC
from datetime import datetime, timezone, timedelta
import time
from typing import Optional

from . import models
from .errors import ItemNotFoundError, ScenarioTimeOutError
from .rest_client_base import InsightRestClientBase


# noinspection PyProtectedMember
class InsightExecutionOperations(InsightRestClientBase, ABC):
    def _find_job_for_scenario(self, scenario_id: str) -> Optional[models.Job]:
        """
        Find a job for the given scenario.

        Returns
        -------
        The job for the scenario's execution, if it exists, or None otherwise.
        """
        jobs = self._make_paged_json_request(
            method='GET',
            path=['api', 'jobs'],
            query_params={'scenarioId': scenario_id},
            item_type=models.Job
        )

        if len(jobs) == 0:
            return None

        return jobs[0]

    def _get_job(self, job_id: str) -> models.Job:
        """
        Given a job ID, return the job object. May raise ItemNotFoundError if job no longer present.
        """
        return self._make_json_request(
            method='GET',
            path=['api', 'jobs', job_id],
            response_type=models.Job
        )

    def _wait_for_job(self, job_id: str, timeout: timedelta) -> None:
        """
        Given job ID, periodically poll it until it's finished, or until wait_time has elapsed.
        """
        stop_time = datetime.now(tz=timezone.utc) + timeout
        next_delay = 0.050
        while True:
            #
            try:
                job = self._get_job(job_id)
            except ItemNotFoundError:
                #
                return

            if job.is_finished():
                #
                return

            #
            if datetime.now(tz=timezone.utc) > stop_time:
                raise ScenarioTimeOutError(f"Scenario did not complete within {timeout}")

            #
            delay = min(next_delay, (stop_time - datetime.now(tz=timezone.utc)).total_seconds())
            #
            time.sleep(max(delay, 0.001))

            #
            next_delay = min(next_delay + 0.050, 1)

    def is_scenario_executing(self, scenario_id: str) -> bool:
        """
        Check whether a scenario is currently executing or about to execute.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario to query.

        Returns
        -------
        is_scenario_executing : bool
            `True` if the scenario is current executed or queued for execution, `False` otherwise.

        Raises
        ------
        scenario.InsightServerError
            If the REST client credentials do not have permission to perform this operation, or there is an issue
            communicating with the Insight server.

        Examples
        --------
        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     SCENARIO_ID = '570b9100-46e3-4643-baee-2e24aa538f25'
        ...     while client.is_scenario_executing(SCENARIO_ID):
        ...         print('The scenario is still executing')
        ...         time.sleep(1)
        ...     print('The scenario is no longer executing.')

        See Also
        --------
        scenario.InsightRestClient.execute_scenario
        scenario.InsightRestClient.wait_for_scenario

        Notes
        -----
        If the REST API client credentials do not have permission to see the scenario, or the scenario doesn't
        exist, this function returns `False`.
        """

        #
        job = self._find_job_for_scenario(scenario_id)

        #
        if job is None:
            return False

        #
        return not job.is_finished()

    def execute_scenario(self,
                         scenario_id: str,
                         execution_mode: str = 'RUN',
                         wait_time: Optional[timedelta] = None) -> None:
        """
        Execute the scenario, optionally waiting for the job to complete.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario to execute.
        execution_mode : str, default 'RUN'
            The name of the execution mode to execute. Defaults to 'RUN' if unset.
        wait_time : timedelta, optional
            Amount of time to wait for scenario to complete. If not specified, the function returns
            immediately.

        Raises
        ------
        scenario.ScenarioTimeOutError
            If the Insight scenario execution did not complete within the given wait time.
        scenario.InsightServerError
            If the REST client credentials do not have permission to perform this operation, or there is an issue
            communicating with the Insight server.

        Examples
        --------
        Execute the scenario and wait up to 30 minutes for it to complete.

        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.execute_scenario('570b9100-46e3-4643-baee-2e24aa538f25',
        ...                             wait_time=timedelta(minutes=30))

        See Also
        --------
        scenario.InsightRestClient.is_scenario_executing

        Notes
        -----
        If a wait time is specified, the function blocks waiting for the scenaio and raises a ScenarioTimeOutError if
        the scenario execution does not finish within the specified time. Note the job is not automatically cancelled,
        so you must call :fct-ref:`scenario.InsightRestClient.cancel_job` if you need to do this.

        If a `wait_time` value is not specified, the function returns immediately after the job is accepted by the
        Insight server.

        This function does not check whether any errors were encountered during the execution of the scenario.
        """

        #
        job = self._make_json_request(
            method='POST',
            path=['api', 'jobs'],
            request_body=models.JobCreationRequest(
                execution_mode=execution_mode,
                scenario=models.Reference(
                    id=scenario_id,
                    object_type='SCENARIO'
                ),
            ),
            expected_status_code=201,
            response_type=models.Job
        )

        #
        if wait_time is not None:
            self._wait_for_job(job.id, wait_time)

    def wait_for_scenario(self,
                         scenario_id: str,
                         timeout: timedelta) -> None:
        """
        Wait until any queued or in-progress scenario execution has completed.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario being executed.
        timeout : timedelta
            Amount of time to wait for scenario to complete.

        Raises
        ------
        scenario.ScenarioTimeOutError
            If the Insight scenario execution did not complete within the given wait time.
        scenario.InsightServerError
            If the REST client credentials do not have permission to perform this operation, or there is an issue
            communicating with the Insight server.

        Examples
        --------
        Wait up to 30 minutes for the scenario to complete.

        >>> with ins.InsightRestClient(insight_url='http://localhost:8080/') as client:
        ...     client.wait_for_scenario('570b9100-46e3-4643-baee-2e24aa538f25',
        ...                              timedelta(minutes=30))

        See Also
        --------
        scenario.InsightRestClient.is_scenario_executing
        scenario.InsightRestClient.execute_scenario

        Notes
        -----
        If the scenario is still queued or executing after the timeout period has elapsed, `ScenarioTimeOutError`
        is raised.

        If the scenario is not queued or executing when this function is called, it returns immediately.
        """

        #
        job = self._find_job_for_scenario(scenario_id)

        #
        if job is not None:
            self._wait_for_job(job.id, timeout)

    def cancel_scenario_execution(self, scenario_id: str) -> None:
        """
        Instructs Insight server to cancel any execution of the given scenario.

        Parameters
        ----------
        scenario_id : str
            The ID of the scenario to cancel.

        Raises
        ------
        scenario.InsightServerError
            If the REST client credentials do not have permission to perform this operation, or there is an issue
            communicating with the Insight server.

        Notes
        -----
        If there is no job found for the current scenario, no error is raised.
        """

        #
        job = self._find_job_for_scenario(scenario_id)
        if job is None:
            return  #

        #
        try:
            self._make_json_request(
                method='DELETE',
                path=['api', 'jobs', job.id],
                expected_status_code=202,
                response_type=None
            )
        except ItemNotFoundError:
            #
            pass
