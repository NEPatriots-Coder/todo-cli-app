#!/usr/bin/env python3
"""TODO CLI Application.

A simple command-line todo list manager with JSON file storage.
"""

import argparse
import sys
from datetime import datetime

from storage import load_todos, save_todos, get_next_id


def parse_date(date_str: str) -> str | None:
    """Parse and validate a date string.

    Args:
        date_str: Date string in YYYY-MM-DD format.

    Returns:
        The validated date string, or None if invalid.
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        return None


def add_todo(task: str, due: str | None = None) -> None:
    """Add a new todo item.

    Args:
        task: The task description.
        due: Optional due date in YYYY-MM-DD format.
    """
    if not task.strip():
        print("Error: Task description cannot be empty.")
        sys.exit(1)

    if due is not None:
        if parse_date(due) is None:
            print("Error: Invalid date format. Use YYYY-MM-DD.")
            sys.exit(1)

    todos = load_todos()
    new_todo = {
        "id": get_next_id(todos),
        "task": task.strip(),
        "completed": False,
        "due": due,
    }
    todos.append(new_todo)
    save_todos(todos)

    due_str = f" (due: {due})" if due else ""
    print(f"Added todo #{new_todo['id']}: {new_todo['task']}{due_str}")


def list_todos(show_all: bool = False) -> None:
    """List todo items.

    Args:
        show_all: If True, show all todos including completed ones.
                  If False, show only pending todos.
    """
    todos = load_todos()

    if not todos:
        print("No todos found.")
        return

    if show_all:
        filtered = todos
    else:
        filtered = [t for t in todos if not t.get("completed", False)]

    if not filtered:
        print("No pending todos." if not show_all else "No todos found.")
        return

    for todo in filtered:
        status = "[x]" if todo.get("completed", False) else "[ ]"
        due_str = f" (due: {todo['due']})" if todo.get("due") else ""
        print(f"{status} #{todo['id']}: {todo['task']}{due_str}")


def complete_todo(todo_id: int) -> None:
    """Mark a todo item as completed.

    Args:
        todo_id: The ID of the todo to complete.
    """
    todos = load_todos()

    for todo in todos:
        if todo.get("id") == todo_id:
            if todo.get("completed", False):
                print(f"Todo #{todo_id} is already completed.")
                return
            todo["completed"] = True
            save_todos(todos)
            print(f"Completed todo #{todo_id}: {todo['task']}")
            return

    print(f"Error: Todo #{todo_id} not found.")
    sys.exit(1)


def delete_todo(todo_id: int) -> None:
    """Delete a todo item.

    Args:
        todo_id: The ID of the todo to delete.
    """
    todos = load_todos()

    for i, todo in enumerate(todos):
        if todo.get("id") == todo_id:
            deleted = todos.pop(i)
            save_todos(todos)
            print(f"Deleted todo #{todo_id}: {deleted['task']}")
            return

    print(f"Error: Todo #{todo_id} not found.")
    sys.exit(1)


def main() -> None:
    """Main entry point for the TODO CLI application."""
    parser = argparse.ArgumentParser(
        description="A simple command-line TODO application."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("task", type=str, help="The task description")
    add_parser.add_argument(
        "--due", "-d",
        type=str,
        default=None,
        help="Due date in YYYY-MM-DD format",
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List todos")
    list_parser.add_argument(
        "--all", "-a",
        action="store_true",
        dest="show_all",
        help="Show all todos including completed ones",
    )

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark a todo as completed")
    complete_parser.add_argument("id", type=int, help="The todo ID to complete")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a todo")
    delete_parser.add_argument("id", type=int, help="The todo ID to delete")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "add":
        add_todo(args.task, args.due)
    elif args.command == "list":
        list_todos(args.show_all)
    elif args.command == "complete":
        complete_todo(args.id)
    elif args.command == "delete":
        delete_todo(args.id)


if __name__ == "__main__":
    main()
