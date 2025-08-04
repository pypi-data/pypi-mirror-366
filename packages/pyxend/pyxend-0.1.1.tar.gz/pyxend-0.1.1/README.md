# pyxend
<p align="center">
  <img src="https://img.shields.io/pypi/v/pyxend" alt="PyPI Version">
  <img src="https://img.shields.io/pypi/l/pyxend" alt="License">
  <img src="https://img.shields.io/pypi/pyversions/pyxend" alt="Python Versions">
  <img src="https://img.shields.io/github/last-commit/codeFlane/pyxend" alt="Last Commit">
  <img src="https://img.shields.io/github/stars/codeFlane/pyxend?style=social" alt="GitHub Stars">
  <img src="https://img.shields.io/badge/VSC-Compatible-blueviolet" alt="VS Code Compatible">
  <img src="https://img.shields.io/badge/Language-Python-blue" alt="Written in Python">
</p>
pyxend is a Pytho
pyxend is a Python-based framework and CLI tool for building Visual Studio Code extensions entirely in Python. It allows developers to define extension commands using simple Python decorators and handle VS Code actions like modifying editor content, showing modals, and running terminal commands.

> ⚡️ No JavaScript required for extension logic — write VS Code extensions in pure Python.

![Preview](https://raw.githubusercontent.com/codeFlane/pyxend/main/preview.gif)
---

## ✨ Features

- 🧠 Simple Python API for defining commands
- ⚙️ CLI tool to scaffold, sync, build, and publish extensions
- 🧩 Template-based generation of `extension.js` and `package.json`
- 🔁 Context-aware Python execution with editor data (selected text, cursor, file)
- 📦 Easy packaging using `vsce`

---

## 📦 Installation

```bash
pip install pyxend
```
Or using git repository:
```bash
git clone https://github.com/codeflane/pyxend
cd pyxend
pip install -e .
```
Make sure Node.js and vsce are installed:
```
npm install -g vsce
```

## 🚀 Getting Started
### 1. Create a new extension
```bash
pyxend init "My Extension Name" myextension
```

### 2. Add logic in Python

Edit main.py:
```python
from pyxend import Extension, ModalType

ext = Extension()

@ext.command('hello')
def say_hello(ctx):
    ext.show_modal("Hello from Python!", type=ModalType.INFO)

ext.run()
```

### 3. Sync the metadata
```bash
pyxend sync
```

### 4. Build and install the extension
```bash
pyxend build
code --install-extension your-extension.vsix
```

## 📚 CLI Options
All CLI commands accept a `--target` (or `-t`) option to specify the working directory (defaults to current folder).

### Init
```bash
pyxend init "Display Name" extension_name
```
Init new project.

#### Arguments:
 - **Display Name:** extension display name (that showing in extension hub)
 - **Extension Name:** extension name (defaults to display name)

#### Creates:
 - `main.py` (logic)
 - `extension.js` (bridge)
 - `package.json` (extension metadata)
 - `.vscodeignore`

### Sync
```bash
pyxend sync
```
Sync Python decorators in main.py with `extension.js` and `package.json`

### Manifest
```bash
pyxend manifest -v 0.0.1 -e 1.70.0 -d desc -t title -n name -g git
```
Update package.json metadata

#### Options:
| Option              | Description                   |
| ------------------- | ----------------------------- |
| `--engine / -e`      | VS Code engine version        |
| `--description / -d` | Description of your extension |
| `--git / -g`         | GitHub repo URL               |
| `--name / -n`        | Display name                  |
| `--version / -v`     | Extension version             |

### License
```bash
pyxend license author
```
Create LICENSE file (now only MIT support).
License is required for creating extensions


## 🧩 Extension API
The core API is exposed via the `Extension` class.

### Command decorator

Decorator to register a command that can be invoked from VS Code.

#### Arguments:

* `name` – The command name (e.g., `"sayHello"`).
* `title` – Title to display in the Command Palette. Defaults to `name`

#### Context:

When the command is invoked, it receives a `context` dictionary with useful metadata:

```json
{
  "selected_text": "Hello",
  "language": "python",
  "cursor_pos": {"line": 3, "character": 15},
  "file_path": "D:/projects/example.py",
  "all_text": "Hello World"
}
```

#### Example:

```python
@ext.command("sayHello", title="Say Hello")
def say_hello(context):
    ext.show_modal(f"Hi! You selected: {context['selected_text']}")
```

---
### Show modal
Show modal popup

#### Arguments:
 - message – The message to display.
 - type – Must be one of the ModalType values:
   - ModalType.INFO
   - ModalType.WARNING
   - ModalType.ERROR

#### Make sure to import ModalType:
```python
from pyxend import ModalType
```
#### Example:
```python
ext.show_modal("This is an error", type=ModalType.error) #Show error modal with text "This is an error"
```

---
### Replace selected text
Replace the currently selected text in the editor.

#### Arguments:
* `text` – The text that will replace the current selection.

#### Example:
```python
ext.replace_selected_text("Replaced content.") #Replace currently selected text to "Replace content."
```

---
### Insert text
Insert text at the current cursor position.

#### Arguments:
* `text` – The text to insert.

#### Example:
```python
ext.insert_text("Inserted text.") #Insert text "Inserted text." after cursor position
```

---
### Open file
Open a file in the editor by its path.

#### Arguments:
* `path` – Full path to the file.

#### Example:
```python
ext.open_file("D:/projects/example.py") #open "D:/projects/example.py" in editor
```

---
### Set cursor position
Move the editor’s cursor to the specified position.

#### Arguments:
* `line` – Line number.
* `character` – Character number.

#### Example:
```python
ext.set_cursor_pos(5, 10) #move cursor to line 5, character 10
```

---
### Save file
Save the current file.

#### Example:
```python
ext.save_file() #save current file
```

---
### Replace all text
Replace the entire content of the file.

#### Arguments:
* `text` – The new content for the whole file.

#### Example:
```python
ext.replace_text("print('Hello, World!')\n") #replace all file text to "print('Hello, World!')"
```

---
### Run terminal command

`ext.run_terminal_command(command: str, name: str = 'pyxend terminal')`
Execute a command in a new or existing terminal.

#### Arguments:
* `command` – The terminal command to execute.
* `name` (optional) – Name of the terminal instance. Default is "pyxend terminal"

#### Example:
```python
ext.run_terminal_command("echo 'Hello World'") #create new terminal and echo "Hello World"
```