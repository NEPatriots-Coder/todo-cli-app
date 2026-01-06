# TODO CLI App

A simple command-line TODO application built with Python. Manage your tasks directly from the terminal with support for adding, listing, completing, and deleting todos.

## Requirements

- Python 3.10+
- pytest (for running tests)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/NEPatriots-Coder/todo-cli-app.git
   cd todo-cli-app
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install test dependencies:
   ```bash
   pip install pytest
   ```

## Usage

### Add a Todo
```bash
python todo.py add "Your task description"
```
Example:
```bash
python todo.py add "Buy groceries"
# Output: Added todo #1: Buy groceries
```

### List Todos
```bash
python todo.py list          # Show pending todos only
python todo.py list --all    # Show all todos (including completed)
```
Example:
```bash
python todo.py list
# Output:
# [ ] #1: Buy groceries
# [ ] #2: Walk the dog
```

### Complete a Todo
```bash
python todo.py complete <id>
```
Example:
```bash
python todo.py complete 1
# Output: Completed todo #1: Buy groceries
```

### Delete a Todo
```bash
python todo.py delete <id>
```
Example:
```bash
python todo.py delete 2
# Output: Deleted todo #2: Walk the dog
```

## Data Storage

Todos are stored in `~/.todos.json` in your home directory, making them accessible from any location on your system.

## Project Structure

| File | Description |
|------|-------------|
| `todo.py` | Main CLI application. Handles command-line argument parsing using argparse and implements the core todo operations (add, list, complete, delete). Entry point for the application. |
| `storage.py` | Storage module for JSON file operations. Provides functions to load todos from disk, save todos to disk, and generate unique IDs for new items. Abstracts file I/O from the main application. |
| `test_todo.py` | Test suite for the CLI application. Contains 18 tests covering all todo operations, output formatting, and error handling scenarios. |
| `test_storage.py` | Test suite for the storage module. Contains 12 tests for file operations including edge cases like missing files, invalid JSON, and ID generation. |

## Running Tests

```bash
source venv/bin/activate
pytest -v
```

All 30 tests should pass:
```
test_storage.py - 12 tests (load, save, get_next_id)
test_todo.py    - 18 tests (add, list, complete, delete)
```

## License

MIT
