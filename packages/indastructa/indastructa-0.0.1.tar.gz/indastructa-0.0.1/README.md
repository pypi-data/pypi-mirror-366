# Indastructa

**Indastructa** is a convenient CLI tool for quickly creating a clear ASCII tree of your project's file structure.

Perfect for documentation, technical reviews, architecture discussions, or blog posts.

---

## Key Features

* **Clear Output:** Generates a beautiful and easy-to-read ASCII tree.
* **Automatic Saving:** The result is automatically saved to a `project_structure.txt` file in the project root.
* **Smart Exclusions:** By default, it ignores unnecessary files and folders (such as `.git`, `venv`, `__pycache__`, `.idea`, and others).
* **Integration with `.gitignore`:** Automatically reads rules from `.gitignore` and `.dockerignore` to exclude everything unrelated to source code.
* **Flexible Configuration:** Allows specifying target folder, limiting scan depth, and adding custom exclusions via command-line arguments.

---

## Installation

```text

pip install indastructa

```
---

## How to Use

### Simple Run

```text

cd /path/to/your/project
indastructa
```

### Example

If your project structure looks like this:

```text

    my_project/
    ├── src/
    │   ├── main.py
    │   └── utils.py
    ├── tests/
    │   └── test_main.py
    ├── .venv/
    ├── .gitignore
    └── README.md
```

indastructa will generate:

```text 

    my_project
    ├── src
    │   ├── main.py
    │   └── utils.py
    ├── tests
    │   └── test_main.py
    ├── .gitignore
    └── README.md
    
    The project structure is saved to the file: `project_structure.txt`
```

---

## Advanced Usage

- Specify a target folder:

```text

indastructa ./src
```
- Limit scan depth (for example, to 2 levels):

```text

indastructa --level 2
```
- Exclude files/folders by pattern:

```text

indastructa --exclude "*.md,docs"
```

---

## Exclusion Logic

`indastructa` uses a three-level filtering system:

1. **Built-in rules:** `.git`, `venv`, `__pycache__`, `dist`, `build`, etc.
2. **Rules from `.gitignore` and `.dockerignore`:** Automatically loaded.
3. **User rules:** Passed via `--exclude` and have the highest priority.

---

## Future Ideas

- Adding info badges (shields.io)
- Interactive mode for excluding files/folders
- Support for exporting structure to JSON/YAML

Have ideas or found a bug? Create an Issue on GitHub.

---

## License

The project is distributed under the MIT License.
