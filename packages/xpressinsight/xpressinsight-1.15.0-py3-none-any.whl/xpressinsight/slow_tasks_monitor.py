"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    This provides a utility for timing an 'operation' and echoing out a warning
    if the time it takes is greater than a configured threshold.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2024-2025 Fair Isaac Corporation. All rights reserved.
"""
from contextlib import contextmanager
from datetime import timedelta
from time import perf_counter
from typing import Callable
import sys

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self


class SlowTasksMonitor:
    """
    SlowTasksMonitor module times how long operations take and emits warnings if the time taken
    is greater than a configured threshold.
    """
    def __init__(self, warning_threshold: timedelta, emit_warning: Callable[[str], None] = print):
        """
        Initialize the SlowTasksMonitor module.

        Parameters
        ----------
        warning_threshold : timedelta
            A warning will be emitted if a task takes longer than the given threshold.
        emit_warning : Callable[[str], None], default print
            A callable to which warning messages will be sent. If unspecified, the 'print'
            statement will be used.
        """
        self.__warning_threshold = warning_threshold.total_seconds()
        self.__emit_warning = emit_warning

    @property
    def warning_threshold(self) -> timedelta:
        """ Read the warning threshold value being used by the monitor. """
        return timedelta(seconds=self.__warning_threshold)

    @contextmanager
    def task(self, task_name: str) -> None:
        """
        Returns a context manager that will emit a warning if it is not closed within the given threshold.

        Parameters
        ----------
        task_name : str
            Name of the task. Will be included in the warning message if the task takes longer than the
            threshold, so should be something meaningful.

        Returns
        -------
        context_manager: None
            A context manager.  The object itself is not meaningful.

        Examples
        --------
        >>> with tasks_monitor.task('Reading from file xyz.txt'):
        ...    with open('xyz.txt', 'r') as f:
        ...        content = f.read()
        """
        start_time = perf_counter()
        yield None
        end_time = perf_counter()
        elapsed_time = end_time - start_time

        if elapsed_time >= self.__warning_threshold:
            self.__emit_warning(f'Task "{task_name}" completed in {elapsed_time}s')

    @classmethod
    def default(cls) -> Self:
        """ Construct and return a task monitor with some default settings. """
        return SlowTasksMonitor(warning_threshold=timedelta(minutes=2), emit_warning=print)
