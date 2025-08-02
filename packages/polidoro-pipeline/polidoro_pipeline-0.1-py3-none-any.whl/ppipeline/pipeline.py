"""
Pipeline module for parallel data processing.

This module provides a Pipeline class that allows for processing data through a sequence
of steps (functions) in parallel. It's designed to handle both single values and lists
of values, automatically parallelizing the processing when possible.

The Pipeline class uses Python's ThreadPoolExecutor for parallel execution and provides
a simple interface for defining and executing processing pipelines.
"""

import os
import threading
import time
from collections.abc import Iterable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any, Callable, Iterator, TypeVar

# Type variables for generic typing
T = TypeVar("T")


class EmptyPipelineError(Exception):
    """Exception raised when attempting to run a pipeline without any steps."""


class InvalidThreadCountError(Exception):
    """Exception raised when an invalid string thread count is passed to the Pipeline."""


def _to_list(data: T | Iterable[T]) -> Iterable[T]:
    """
    Convert input data to a list if it's not already a list.

    Args:
        data: Any data that needs to be ensured as a list

    Returns:
        The input data as a list
    """
    if isinstance(data, Iterable) and not isinstance(data, (dict, str)):
        return data
    return [data]


class Pipeline:
    """
    A parallel processing pipeline that executes a series of steps on input data.

    The Pipeline class allows for processing data through a sequence of steps (functions)
    where each step can be executed in parallel using a thread pool. The pipeline can
    handle both single values and lists of values, automatically parallelizing the
    processing when possible.
    """

    def __init__(
        self, steps: list[Callable] | None = None, thread_count: int | str | None = None
    ) -> None:
        """
        Initialize a new Pipeline instance.

        Args:
            steps: A list of callable functions to be executed in sequence
            thread_count: The maximum number of worker threads to use for parallel processing.
                          If None, uses the default ThreadPoolExecutor behavior.
        """
        self.steps = steps or []
        self._running_tasks = 1
        self.lock = threading.Lock()
        if isinstance(thread_count, str):
            if thread_count[0] == "x":
                thread_count = int(thread_count[1:]) * os.cpu_count()
            else:
                raise InvalidThreadCountError(
                    f"Invalid thread count string: {thread_count}"
                )

        self.thread_count = thread_count

    def add_step(self, step: Callable) -> None:
        """
        Add a processing step to the pipeline.

        Args:
            step: A callable function that will be added to the end of the pipeline
        """
        self.steps.append(step)

    def run(self, data: Any | list[Any]) -> Iterator[Any]:
        """
        Execute the pipeline on the provided data.

        This method processes the input data through all steps in the pipeline.
        If the input is a list, each item will be processed in parallel.
        Each step can also return multiple items (as a list) which will be
        processed independently in subsequent steps.

        Args:
            data: The input data to process, can be a single value or a list of values

        Returns:
            An iterator of results after processing through all pipeline steps

        Raises:
            EmptyPipelineError: If the pipeline has no steps
        """
        # Check if the pipeline has any steps
        if not self.steps:
            raise EmptyPipelineError("Cannot run pipeline without steps")

        # Create thread pool for parallel execution
        executor = ThreadPoolExecutor(max_workers=self.thread_count)

        # List to collect final results
        results: list[Future[Any]] = []

        # Start the pipeline by processing the initial data
        self._callback(data, executor, 0, results)

        # Wait until all tasks are completed
        # The _running_tasks counter is updated by _callback method
        while True:
            with self.lock:
                if self._running_tasks == 0:
                    break
            # Small sleep to avoid busy waiting
            time.sleep(0.01)

        # Yield results as they complete
        for r in as_completed(results):
            yield r.result()

    def _callback(
        self,
        future: Future | Any,
        executor: ThreadPoolExecutor,
        step_index: int,
        results: list[Future[Any]],
    ) -> None:
        """
        Internal callback method to handle the results of each step and chain to the next step.

        Args:
            future: Either a Future object containing the result of a previous step,
                   or the initial input data
            executor: The ThreadPoolExecutor instance used for parallel processing
            step_index: The index of the current step in the pipeline
            results: A list to collect the final results of the pipeline
        """
        # Extract result from Future object if needed
        if isinstance(future, Future):
            resp = future.result()
        else:
            # For the initial call, future is the raw input data
            resp = future

        # Ensure we have a list to process, even if the result was a single item
        new_data = _to_list(resp)

        new_tasks = []
        for data in new_data:
            # Submit the current step to the executor
            new_tasks.append(executor.submit(self.steps[step_index], data))
        # Update the running tasks counter
        # We're about to process len(new_data) items, but we're finishing one task,
        # so the net change is len(new_data) - 1
        with self.lock:
            self._running_tasks += len(new_tasks) - 1

        # Process each item in the data
        for task in new_tasks:
            if step_index < len(self.steps) - 1:
                # If there are more steps, chain to the next step using a callback
                task.add_done_callback(
                    lambda x: self._callback(x, executor, step_index + 1, results)
                )
            else:
                # If this is the last step, collect the result and decrement the task counter
                results.append(task)
                with self.lock:
                    self._running_tasks -= 1
