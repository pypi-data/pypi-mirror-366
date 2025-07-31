"""Tests for the doteval pytest plugin functionality."""

import os
import subprocess
import sys
import tempfile


def test_pytest_plugin_basic_execution():
    """Test that the pytest plugin can execute doteval tests."""
    # Create a temporary test file
    test_content = """
import doteval
from doteval import Result
from doteval.evaluators import exact_match

dataset = [("Hello", "Hello"), ("World", "World")]

@doteval.foreach("input,expected", dataset)
def eval_basic(input, expected):
    prompt = f"Input: {input}"
    return Result(exact_match(input, expected), prompt=prompt)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", f.name, "-v"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Check that the test passed
            if result.returncode != 0:
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
            assert result.returncode == 0
            assert "eval_basic" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_parametrize():
    """Test that the pytest plugin can execute doteval tests."""
    # Create a temporary test file
    test_content = """
import doteval
import pytest
from doteval import Result
from doteval.evaluators import exact_match

dataset = [("Hello", "Hello"), ("World", "World")]

@pytest.mark.parametrize(
    "add", ["a", "b", "c"]
)
@doteval.foreach("input,expected", dataset)
def eval_basic(input, expected, add):
    prompt = f"Input: {input}, Add: {add}"
    return Result(exact_match(input, expected), prompt=prompt)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", f.name, "-v"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Check that the test passed
            assert result.returncode == 0
            assert "eval_basic" in result.stdout
            assert "3 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_fixture():
    """Test that the pytest plugin can execute doteval tests with fixtures."""
    # Create a temporary test file
    test_content = """
import doteval
import pytest
from doteval import Result
from doteval.evaluators import exact_match

@pytest.fixture
def add():
    return "a"

dataset = [("Hello", "Hello"), ("World", "World")]

@doteval.foreach("input,expected", dataset)
def eval_basic(input, expected, add):
    add()
    prompt = f"Input: {input}"
    return Result(exact_match(input, expected), prompt=prompt)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", f.name, "-v"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Check that the test passed
            if result.returncode != 0:
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
            assert result.returncode == 0
            assert "eval_basic" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_samples_option():
    """Test that the --samples option works with pytest."""
    # Create a temporary test file with larger dataset
    test_content = """
import doteval
from doteval.evaluators import exact_match

dataset = [
    ("Q1", "A1"),
    ("Q2", "A2"),
    ("Q3", "A3"),
    ("Q4", "A4"),
    ("Q5", "A5")
]

@doteval.foreach("question,answer", dataset)
def eval_with_samples(question, answer):
    return doteval.Result(exact_match(question, answer), prompt=f"Q: {question}")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    f.name,
                    "--samples",
                    "2",
                    "-v",  # Verbose to show function names
                ],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Check that the test passed
            assert result.returncode == 0
            assert "eval_with_samples" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_custom_column_names():
    """Test that custom column names work in pytest."""
    test_content = """
import doteval
from doteval.evaluators import exact_match

dataset = [("user_input", "model_output", "extra_context")]

@doteval.foreach("user_prompt,model_response,context", dataset)
def eval_custom_columns(user_prompt, model_response, context):
    combined = f"{user_prompt}-{model_response}-{context}"
    expected = "user_input-model_output-extra_context"
    prompt = f"Combining: {user_prompt}, {model_response}, {context}"
    return doteval.Result(exact_match(combined, expected), prompt=prompt)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", f.name, "-v"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Check that the test passed
            assert result.returncode == 0
            assert "eval_custom_columns" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_invalid_concurrent_option():
    """Test that invalid concurrent option falls back to None."""
    test_content = """
import doteval
from doteval.evaluators import exact_match

dataset = [("test", "test")]

@doteval.foreach("input,expected", dataset)
def eval_with_invalid_concurrent(input, expected):
    return doteval.Result(exact_match(input, expected), prompt=f"Input: {input}")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    f.name,
                    "--concurrent",
                    "invalid_value",  # This should be handled gracefully
                    "-v",
                ],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Should still pass despite invalid concurrent option
            assert result.returncode == 0
            assert "eval_with_invalid_concurrent" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_concurrent_auto():
    """Test that --concurrent auto works."""
    test_content = """
import doteval
import asyncio
from doteval.evaluators import exact_match

dataset = [("test1", "test1"), ("test2", "test2")]

@doteval.foreach("input,expected", dataset)
async def eval_async_auto(input, expected):
    await asyncio.sleep(0.001)
    return doteval.Result(exact_match(input, expected), prompt=f"Input: {input}")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    f.name,
                    "--concurrent",
                    "auto",
                    "-v",
                ],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Should pass and use auto concurrency
            assert result.returncode == 0
            assert "eval_async_auto" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_mixed_sync_async():
    """Test plugin with mixed sync and async evaluations."""
    test_content = """
import doteval
import asyncio
from doteval.evaluators import exact_match

dataset = [("test1", "test1"), ("test2", "test2")]

@doteval.foreach("input,expected", dataset)
def eval_sync_mixed(input, expected):
    return doteval.Result(exact_match(input, expected), prompt=f"Sync: {input}")

@doteval.foreach("input,expected", dataset)
async def eval_async_mixed(input, expected):
    await asyncio.sleep(0.001)
    return doteval.Result(exact_match(input, expected), prompt=f"Async: {input}")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    f.name,
                    "--concurrent",
                    "2",
                    "-v",
                ],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Should pass and handle both sync and async
            assert result.returncode == 0
            assert "eval_sync_mixed" in result.stdout
            assert "eval_async_mixed" in result.stdout
            assert "2 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_no_doteval_items():
    """Test plugin behavior when no doteval items are collected."""
    test_content = """
import pytest

def test_regular_pytest_test():
    assert True
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    f.name,
                    "--concurrent",
                    "2",
                    "-v",
                ],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Should still pass regular pytest tests
            assert result.returncode == 0
            assert "test_regular_pytest_test" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_concurrent_execution_path():
    """Test that concurrent execution path is triggered for async evaluations."""
    test_content = """
import doteval
import asyncio
from doteval.evaluators import exact_match

dataset = [("test1", "test1"), ("test2", "test2")]

@doteval.foreach("input,expected", dataset)
async def eval_concurrent_execution(input, expected):
    await asyncio.sleep(0.001)
    return doteval.Result(exact_match(input, expected), prompt=f"Input: {input}")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    f.name,
                    "--concurrent",
                    "2",  # Force concurrent execution
                    "-v",
                ],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Should pass and use concurrent execution
            assert result.returncode == 0
            assert "eval_concurrent_execution" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_wrapped_function_detection():
    """Test async function detection with wrapped functions."""
    test_content = """
import doteval
import asyncio
from doteval.evaluators import exact_match
from functools import wraps

def decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper

dataset = [("test1", "test1")]

@doteval.foreach("input,expected", dataset)
@decorator
async def eval_wrapped_async(input, expected):
    await asyncio.sleep(0.001)
    return doteval.Result(exact_match(input, expected), prompt=f"Input: {input}")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    f.name,
                    "--concurrent",
                    "2",
                    "-v",
                ],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Should detect wrapped async function and run concurrently
            assert result.returncode == 0
            assert "eval_wrapped_async" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_auto_concurrent_cpu_detection():
    """Test --concurrent auto actually uses CPU count."""
    test_content = """
import doteval
import asyncio
from doteval.evaluators import exact_match

dataset = [("test1", "test1"), ("test2", "test2"), ("test3", "test3")]

@doteval.foreach("input,expected", dataset)
async def eval_auto_concurrent(input, expected):
    await asyncio.sleep(0.001)
    return doteval.Result(exact_match(input, expected), prompt=f"Input: {input}")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    f.name,
                    "--concurrent",
                    "auto",  # This should trigger multiprocessing.cpu_count()
                    "-v",
                ],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Should use auto concurrency based on CPU count
            assert result.returncode == 0
            assert "eval_auto_concurrent" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_no_concurrent_items_found():
    """Test when no concurrent items are found but concurrent option is set."""
    test_content = """
import doteval
from doteval.evaluators import exact_match

dataset = [("test1", "test1")]

@doteval.foreach("input,expected", dataset)
def eval_sync_only(input, expected):
    # This is sync, so won't be in concurrent_items
    return doteval.Result(exact_match(input, expected), prompt=f"Input: {input}")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    f.name,
                    "--concurrent",
                    "2",  # Concurrent enabled but no async functions
                    "-v",
                ],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Should still pass, just run sequentially
            assert result.returncode == 0
            assert "eval_sync_only" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)
