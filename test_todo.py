"""Tests for the todo CLI application."""

import os
import tempfile
from unittest import mock

import pytest

import storage
from todo import add_todo, list_todos, complete_todo, delete_todo, parse_date


@pytest.fixture
def temp_storage(monkeypatch):
    """Use a temporary file for storage during tests."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.remove(path)  # Start with no file
    monkeypatch.setattr(storage, "DEFAULT_FILEPATH", path)
    yield path
    if os.path.exists(path):
        os.remove(path)


class TestAddTodo:
    """Tests for add_todo function."""

    def test_add_creates_todo(self, temp_storage: str, capsys) -> None:
        """Adding a todo creates it in storage."""
        add_todo("Test task")
        todos = storage.load_todos(temp_storage)
        assert len(todos) == 1
        assert todos[0]["task"] == "Test task"
        assert todos[0]["completed"] is False
        assert todos[0]["id"] == 1

    def test_add_prints_confirmation(self, temp_storage: str, capsys) -> None:
        """Adding a todo prints confirmation message."""
        add_todo("Test task")
        captured = capsys.readouterr()
        assert "Added todo #1: Test task" in captured.out

    def test_add_multiple_todos(self, temp_storage: str) -> None:
        """Adding multiple todos assigns sequential IDs."""
        add_todo("First")
        add_todo("Second")
        add_todo("Third")
        todos = storage.load_todos(temp_storage)
        assert len(todos) == 3
        assert todos[0]["id"] == 1
        assert todos[1]["id"] == 2
        assert todos[2]["id"] == 3

    def test_add_empty_task_exits(self, temp_storage: str) -> None:
        """Adding empty task exits with error."""
        with pytest.raises(SystemExit) as exc_info:
            add_todo("   ")
        assert exc_info.value.code == 1

    def test_add_strips_whitespace(self, temp_storage: str) -> None:
        """Task description is stripped of leading/trailing whitespace."""
        add_todo("  Spaced task  ")
        todos = storage.load_todos(temp_storage)
        assert todos[0]["task"] == "Spaced task"


class TestListTodos:
    """Tests for list_todos function."""

    def test_list_empty(self, temp_storage: str, capsys) -> None:
        """Listing with no todos shows appropriate message."""
        list_todos()
        captured = capsys.readouterr()
        assert "No todos found" in captured.out

    def test_list_shows_pending(self, temp_storage: str, capsys) -> None:
        """Listing shows pending todos."""
        add_todo("Pending task")
        capsys.readouterr()  # Clear add output
        list_todos()
        captured = capsys.readouterr()
        assert "[ ] #1: Pending task" in captured.out

    def test_list_hides_completed_by_default(self, temp_storage: str, capsys) -> None:
        """Completed todos are hidden by default."""
        add_todo("Task 1")
        add_todo("Task 2")
        complete_todo(1)
        capsys.readouterr()  # Clear previous output
        list_todos()
        captured = capsys.readouterr()
        assert "#1" not in captured.out
        assert "#2" in captured.out

    def test_list_all_shows_completed(self, temp_storage: str, capsys) -> None:
        """List with --all shows completed todos."""
        add_todo("Task 1")
        complete_todo(1)
        capsys.readouterr()  # Clear previous output
        list_todos(show_all=True)
        captured = capsys.readouterr()
        assert "[x] #1: Task 1" in captured.out

    def test_list_no_pending_message(self, temp_storage: str, capsys) -> None:
        """Shows 'no pending' when all are completed."""
        add_todo("Task 1")
        complete_todo(1)
        capsys.readouterr()
        list_todos()
        captured = capsys.readouterr()
        assert "No pending todos" in captured.out


class TestCompleteTodo:
    """Tests for complete_todo function."""

    def test_complete_marks_done(self, temp_storage: str) -> None:
        """Completing a todo marks it as completed."""
        add_todo("Test task")
        complete_todo(1)
        todos = storage.load_todos(temp_storage)
        assert todos[0]["completed"] is True

    def test_complete_prints_confirmation(self, temp_storage: str, capsys) -> None:
        """Completing a todo prints confirmation."""
        add_todo("Test task")
        capsys.readouterr()
        complete_todo(1)
        captured = capsys.readouterr()
        assert "Completed todo #1" in captured.out

    def test_complete_already_completed(self, temp_storage: str, capsys) -> None:
        """Completing already completed todo shows message."""
        add_todo("Test task")
        complete_todo(1)
        capsys.readouterr()
        complete_todo(1)
        captured = capsys.readouterr()
        assert "already completed" in captured.out

    def test_complete_invalid_id_exits(self, temp_storage: str) -> None:
        """Completing non-existent todo exits with error."""
        add_todo("Test task")
        with pytest.raises(SystemExit) as exc_info:
            complete_todo(999)
        assert exc_info.value.code == 1


class TestDeleteTodo:
    """Tests for delete_todo function."""

    def test_delete_removes_todo(self, temp_storage: str) -> None:
        """Deleting a todo removes it from storage."""
        add_todo("Test task")
        delete_todo(1)
        todos = storage.load_todos(temp_storage)
        assert len(todos) == 0

    def test_delete_prints_confirmation(self, temp_storage: str, capsys) -> None:
        """Deleting a todo prints confirmation."""
        add_todo("Test task")
        capsys.readouterr()
        delete_todo(1)
        captured = capsys.readouterr()
        assert "Deleted todo #1" in captured.out

    def test_delete_invalid_id_exits(self, temp_storage: str) -> None:
        """Deleting non-existent todo exits with error."""
        with pytest.raises(SystemExit) as exc_info:
            delete_todo(999)
        assert exc_info.value.code == 1

    def test_delete_correct_item(self, temp_storage: str) -> None:
        """Deleting removes only the specified todo."""
        add_todo("Task 1")
        add_todo("Task 2")
        add_todo("Task 3")
        delete_todo(2)
        todos = storage.load_todos(temp_storage)
        assert len(todos) == 2
        assert todos[0]["id"] == 1
        assert todos[1]["id"] == 3


class TestParseDate:
    """Tests for parse_date function."""

    def test_valid_date(self) -> None:
        """Valid date string returns the same string."""
        assert parse_date("2025-01-15") == "2025-01-15"

    def test_invalid_format(self) -> None:
        """Invalid date format returns None."""
        assert parse_date("01-15-2025") is None
        assert parse_date("2025/01/15") is None
        assert parse_date("January 15, 2025") is None

    def test_invalid_date(self) -> None:
        """Invalid date values return None."""
        assert parse_date("2025-13-01") is None  # Invalid month
        assert parse_date("2025-01-32") is None  # Invalid day
        assert parse_date("not-a-date") is None


class TestDueDates:
    """Tests for due date functionality."""

    def test_add_with_due_date(self, temp_storage: str, capsys) -> None:
        """Adding a todo with due date stores it correctly."""
        add_todo("Task with deadline", due="2025-01-15")
        todos = storage.load_todos(temp_storage)
        assert todos[0]["due"] == "2025-01-15"

    def test_add_without_due_date(self, temp_storage: str) -> None:
        """Adding a todo without due date sets due to None."""
        add_todo("Task without deadline")
        todos = storage.load_todos(temp_storage)
        assert todos[0]["due"] is None

    def test_add_prints_due_date(self, temp_storage: str, capsys) -> None:
        """Adding a todo with due date shows it in confirmation."""
        add_todo("Task", due="2025-01-15")
        captured = capsys.readouterr()
        assert "(due: 2025-01-15)" in captured.out

    def test_add_invalid_due_date_exits(self, temp_storage: str) -> None:
        """Adding a todo with invalid due date exits with error."""
        with pytest.raises(SystemExit) as exc_info:
            add_todo("Task", due="invalid-date")
        assert exc_info.value.code == 1

    def test_list_shows_due_date(self, temp_storage: str, capsys) -> None:
        """Listing todos displays due dates."""
        add_todo("Task with deadline", due="2025-01-15")
        capsys.readouterr()
        list_todos()
        captured = capsys.readouterr()
        assert "(due: 2025-01-15)" in captured.out

    def test_list_no_due_date_no_extra_text(self, temp_storage: str, capsys) -> None:
        """Listing todos without due dates doesn't show due text."""
        add_todo("Task without deadline")
        capsys.readouterr()
        list_todos()
        captured = capsys.readouterr()
        assert "(due:" not in captured.out
