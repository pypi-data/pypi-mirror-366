import sys
from json import loads, dumps
from enum import Enum

class ModalType(Enum):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'

class Extension:
    def __init__(self) -> None:
        """Init your extension"""
        self.commands = {}
        self.step = 0
        self.actions = []

    def command(self, name: str, title: str | None = None):
        """Command decorator  
        ### Using:
        ```python
        from pyxend import Extension

        ext = Extension()
        @ext.command(COMMAND_NAME, COMMAND_TITLE)
        def COMMAND_NAME(context):
            #your code here
            pass
        ext.run()
        ```

        ### Args:
            **name (str):** command name
            **title (str, optional):** command title. Defaults to None.

        ### Context:
        on function execute, pyxend add context to arguments.  
        Now it contains selected_text, language, cursor_pos, file_path, all_text
        #### Example:
        ```python
        @ext.command('getContext')
        def get_context(context):
            print(context)
        ```
        -> `{'selected_text': 'hello', 'language': 'text', 'cursor_pos': {'line': 1, 'character': 4}, 'file_path': 'D:\test.txt', 'all_text': 'Hello, world'}`
        """
        def decorator(fn):
            """Decorator for command"""
            self.commands[name] = fn
            return fn
        return decorator

    def show_modal(self, message: str, type: ModalType = ModalType.INFO) -> None:
        """Show modal

        ### Args:
            **message (str):** message
            **type (ModalType):** modal type (info, warning or error)
        """
        self.actions.append({"action": "show_modal", "message": message, "type": type.value})

    def replace_selected_text(self, text: str) -> None:
        """Replace selected text

        ### Args:
            **text (str):** text to replace
        """
        self.actions.append({"action": "replace_selected_text", "text": text})

    def insert_text(self, text: str) -> None:
        """Insert text after cursor

        ### Args:
            **text (str):** text to insert
        """
        self.actions.append({"action": "insert_text", "text": text})

    def open_file(self, path: str) -> None:
        """Open file in editor

        ### Args:
            **path (str):** file path
        """
        self.actions.append({"action": "open_file", "path": path})

    def set_cursor_pos(self, line: int, character: int) -> None:
        """Set cursor position

        ### Args:
            **line (int):** line number
            **character (int):** character number
        """
        self.actions.append({"action": "set_cursor_pos", "line": line, 'character': character})

    def save_file(self) -> None:
        """Save file

        ### Args:
            No args required
        """
        self.actions.append({"action": "save_file"})

    def replace_text(self, text: str) -> None:
        """Replace all text from file

        ### Args:
            **text (str):** text to replace
        """
        self.actions.append({"action": "overwrite_file", "text": text})

    def run_terminal_command(self, command: str, name: str = 'pyxend terminal') -> None:
        """Run terminal command (create terminal, show it, execute command)

        ### Args:
            **command (str):** command to execute
            **name (str, optional):** terminal name. Defaults to pyxend terminal
        """
        self.actions.append({"action": "run_terminal_command", "command": command, "terminal_name": name})

    def run(self) -> None:
        """Run your extension  
        If you want to test extension, execute as `python main.py COMMAND_NAME CONTEXT`
        """
        args = sys.argv[1:]
        if not args:
            print(dumps({"error": "Missing command"}))
            return
        if len(args) < 2:
            print(dumps({'error': 'Missing context'}))
            return

        command = args[0]
        if command in self.commands:
            try:
                context = loads(args[1])
            except Exception as e:
                print(dumps({'error': f'Invalid JSON context: {str(e)}'}))
                return
            self.commands[command](context)
            print(dumps(self.actions))
            self.actions.clear()
        else:
            print(dumps({"error": "Unknown command"}))
