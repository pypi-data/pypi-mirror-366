"""
Tests for the Pipeline class functionality.

This module contains unit tests that verify the behavior of the Pipeline class
from the ppipeline module. The tests cover various aspects including:
- Basic pipeline execution
- Processing lists of values
- Adding steps to a pipeline
- Error handling
- Thread count configuration
"""

import os

import pytest

from ppipeline import Pipeline
from ppipeline.pipeline import EmptyPipelineError, InvalidThreadCountError


def add_1(x: int) -> int:
    """
    Helper function that adds 1 to the input value.

    Args:
        x: The input value

    Returns:
        The input value plus 1
    """
    print("add", x)
    return x + 1


def mul_2(x: int) -> int:
    """
    Helper function that multiplies the input value by 2.

    Args:
        x: The input value

    Returns:
        The input value multiplied by 2
    """
    print("mul", x)
    return x * 2


def test_simple_run() -> None:
    """
    Test basic pipeline execution with a single input value.

    Verifies that a pipeline with two steps (add_1 and mul_2) correctly
    processes a single input value and returns the expected result.
    """
    pipeline = Pipeline([add_1, mul_2])
    assert list(pipeline.run(1)) == [4]


def test_run_with_lists() -> None:
    """
    Test pipeline execution with a list of input values.

    Verifies that a pipeline correctly processes multiple input values
    in parallel and returns the expected results.
    """
    pipeline = Pipeline([add_1, mul_2])
    assert set(pipeline.run([1, 2, 3])) == {4, 6, 8}


def test_add_step() -> None:
    """
    Test adding steps to a pipeline incrementally.

    Verifies that steps can be added to a pipeline after initialization
    and that the pipeline correctly processes input through these steps.
    """
    pipeline = Pipeline()
    pipeline.add_step(add_1)
    pipeline.add_step(mul_2)
    assert list(pipeline.run(2)) == [6]


def test_without_steps() -> None:
    """
    Test error handling when running a pipeline without steps.

    Verifies that attempting to run a pipeline without any steps
    raises an EmptyPipelineError with the appropriate error message.
    """
    pipeline = Pipeline()
    with pytest.raises(EmptyPipelineError, match="Cannot run pipeline without steps"):
        list(pipeline.run(1))


def test_when_error() -> None:
    """
    Test error propagation when a pipeline step raises an exception.

    Verifies that when a function in the pipeline raises an exception,
    the exception is properly propagated to the caller.
    """
    def failing_function(_x: int) -> None:
        """
        Helper function that always raises a ValueError.

        Args:
            _x: The input value (unused)

        Raises:
            ValueError: Always raises this error with message "Test error"
        """
        raise ValueError("Test error")

    # Create a pipeline with just the failing function
    pipeline = Pipeline([failing_function])

    # Verify that the error is propagated
    with pytest.raises(ValueError, match="Test error"):
        list(pipeline.run(1))


def test_passing_thread_count_as_str() -> None:
    """
    Test thread count configuration using string multiplier.

    Verifies that when a thread count is specified as a string with format "xN",
    the pipeline correctly sets the thread count to N times the CPU count.
    """
    pipeline = Pipeline([add_1, mul_2], thread_count="x2")
    assert pipeline.thread_count == 2 * os.cpu_count()


def test_passing_invalid_thread_count_as_str() -> None:
    """
    Test error handling for invalid thread count string format.

    Verifies that when a thread count is specified as a string that doesn't
    follow the expected format "xN", an InvalidThreadCountError is raised.
    """
    with pytest.raises(InvalidThreadCountError, match="Invalid thread count string"):
        Pipeline([add_1, mul_2], thread_count="10")
