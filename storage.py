"""Storage module for TODO CLI application.

Handles reading and writing todos to a JSON file.
"""

import json
import os
from pathlib import Path


DEFAULT_FILEPATH: str = str(Path.home() / ".todos.json")


def load_todos(filepath: str | None = None) -> list[dict]:
    """Load todos from a JSON file.

    Args:
        filepath: Path to the JSON file. Defaults to ~/.todos.json.

    Returns:
        List of todo dictionaries. Returns empty list if file doesn't exist
        or contains invalid JSON.
    """
    if filepath is None:
        filepath = DEFAULT_FILEPATH
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, IOError):
        return []


def save_todos(todos: list[dict], filepath: str | None = None) -> None:
    """Save todos to a JSON file.

    Args:
        todos: List of todo dictionaries to save.
        filepath: Path to the JSON file. Defaults to ~/.todos.json.

    Raises:
        IOError: If the file cannot be written.
    """
    if filepath is None:
        filepath = DEFAULT_FILEPATH
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)


def get_next_id(todos: list[dict]) -> int:
    """Generate the next available ID for a new todo.

    Args:
        todos: List of existing todo dictionaries.

    Returns:
        The next available integer ID (max existing ID + 1, or 1 if empty).
    """
    if not todos:
        return 1
    return max(todo.get("id", 0) for todo in todos) + 1
