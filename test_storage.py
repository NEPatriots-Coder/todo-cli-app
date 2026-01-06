"""Tests for the storage module."""

import json
import os
import tempfile

import pytest

from storage import load_todos, save_todos, get_next_id


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


class TestLoadTodos:
    """Tests for load_todos function."""

    def test_load_from_nonexistent_file(self) -> None:
        """Loading from a non-existent file returns empty list."""
        result = load_todos("/nonexistent/path/todos.json")
        assert result == []

    def test_load_from_empty_file(self, temp_file: str) -> None:
        """Loading from an empty file returns empty list."""
        with open(temp_file, "w") as f:
            f.write("")
        result = load_todos(temp_file)
        assert result == []

    def test_load_from_invalid_json(self, temp_file: str) -> None:
        """Loading from invalid JSON returns empty list."""
        with open(temp_file, "w") as f:
            f.write("not valid json")
        result = load_todos(temp_file)
        assert result == []

    def test_load_from_valid_file(self, temp_file: str) -> None:
        """Loading from valid JSON file returns the data."""
        todos = [{"id": 1, "task": "Test task", "completed": False}]
        with open(temp_file, "w") as f:
            json.dump(todos, f)
        result = load_todos(temp_file)
        assert result == todos

    def test_load_non_list_json(self, temp_file: str) -> None:
        """Loading JSON that isn't a list returns empty list."""
        with open(temp_file, "w") as f:
            json.dump({"key": "value"}, f)
        result = load_todos(temp_file)
        assert result == []


class TestSaveTodos:
    """Tests for save_todos function."""

    def test_save_empty_list(self, temp_file: str) -> None:
        """Saving empty list creates valid JSON file."""
        save_todos([], temp_file)
        with open(temp_file, "r") as f:
            data = json.load(f)
        assert data == []

    def test_save_and_load_roundtrip(self, temp_file: str) -> None:
        """Data saved can be loaded back correctly."""
        todos = [
            {"id": 1, "task": "First task", "completed": False},
            {"id": 2, "task": "Second task", "completed": True},
        ]
        save_todos(todos, temp_file)
        result = load_todos(temp_file)
        assert result == todos

    def test_save_overwrites_existing(self, temp_file: str) -> None:
        """Saving overwrites existing file content."""
        save_todos([{"id": 1, "task": "Old", "completed": False}], temp_file)
        save_todos([{"id": 2, "task": "New", "completed": True}], temp_file)
        result = load_todos(temp_file)
        assert len(result) == 1
        assert result[0]["task"] == "New"


class TestGetNextId:
    """Tests for get_next_id function."""

    def test_empty_list_returns_one(self) -> None:
        """Empty list returns ID of 1."""
        assert get_next_id([]) == 1

    def test_single_item(self) -> None:
        """Single item returns max ID + 1."""
        todos = [{"id": 1, "task": "Test", "completed": False}]
        assert get_next_id(todos) == 2

    def test_multiple_items(self) -> None:
        """Multiple items returns max ID + 1."""
        todos = [
            {"id": 1, "task": "First", "completed": False},
            {"id": 5, "task": "Fifth", "completed": True},
            {"id": 3, "task": "Third", "completed": False},
        ]
        assert get_next_id(todos) == 6

    def test_missing_id_field(self) -> None:
        """Items missing id field are treated as id 0."""
        todos = [{"task": "No ID", "completed": False}]
        assert get_next_id(todos) == 1
