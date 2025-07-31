'''generate ASCII tree representation of your project structure'''

from pathlib import Path
from typing import Set


PROJECT_DIR: Path = Path.cwd()

OUTPUT_FILENAME: Path = Path("project_structure.txt")

# Files and directories to ignore:
EXCLUDE_SET: Set[str] = {
    # General
    ".git", ".idea", ".vscode", ".history", "logs", ".DS_Store",

    # Python
    "__pycache__", ".ruff_cache", ".venv", "venv", "Scripts",
    "*.pyc", "*.egg-info",

    # Node.js
    "node_modules", "dist", "build", ".next",

    # Django
    "migrations", "migrations.py", "migrations_old",

    # Env
    ".env",

    # IDE specific
    ".idea_modules", "atlassian-ide-plugin.xml",

    # This script
    OUTPUT_FILENAME.name,
    Path(__file__).name,
}


def format_dir_structure(root_path: Path, exclude_set: Set[str], prefix: str = "") -> str:
    """
    Recursively builds a string representation of a directory structure.

    Args:
        root_path: The path to the directory to format.
        exclude_set: A set of file and directory names to ignore.
        prefix: The prefix string used for formatting the tree structure.

    Returns:
        A multi-line string representing the directory structure.
    """
    try:
        items = sorted(
            [p for p in root_path.iterdir() if p.name not in exclude_set],
            key=lambda p: (p.is_file(), p.name.lower())
        )
    except FileNotFoundError:
        return f"{prefix}  +-- [Error: Directory not found]"
    except PermissionError:
        return f"{prefix}  +-- [Error: Permission denied]"

    parts = []
    for i, item in enumerate(items):
        is_last = (i == len(items) - 1)
        # Use ASCII characters for wider compatibility
        connector = "  +-- " if is_last else "  |-- "

        item_display_name = f"{item.name}{'/' if item.is_dir() else ''}"
        parts.append(f"{prefix}{connector}{item_display_name}")

        if item.is_dir():
            new_prefix = prefix + ("      " if is_last else "  |   ")
            parts.append(format_dir_structure(item, exclude_set, new_prefix))

    return "\n".join(parts)


def write_structure_to_file(output_file: Path, content: str) -> None:
    """
    Writes the directory structure to a file.

    Args:
        output_file: The file path to write the output to.
        content: The string content to write to the file.
    """
    try:
        output_file.write_text(content, encoding="utf-8")
        print(f"Project structure successfully saved to: {output_file}")
    except IOError as e:
        print(f"Error writing to file {output_file}: {e}")


def main() -> None:
    """
    The main entry point for the script.
    """
    structure_text = format_dir_structure(PROJECT_DIR, EXCLUDE_SET)
    output_content = f"{PROJECT_DIR.name}/\n{structure_text}\n"

    write_structure_to_file(OUTPUT_FILENAME, output_content)

    print("\n--- File Content ---")
    print(output_content)


if __name__ == "__main__":
    main()
