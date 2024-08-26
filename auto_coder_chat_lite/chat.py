import json
import os
import sys
from typing import List
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from rich.console import Console
from rich.table import Table

# 模拟内存存储
memory = {
    "current_files": {"files": []},
    "conf": {},
}

commands = [
    "/add_files",
    "/remove_files",
    "/list_files",
    "/coding",
    "/help",
    "/exit",
]

def get_all_file_names_in_project() -> List[str]:
    project_root = os.getcwd()
    file_names = []
    for root, dirs, files in os.walk(project_root):
        file_names.extend(files)
    return file_names

def find_files_in_project(patterns: List[str]) -> List[str]:
    project_root = os.getcwd()
    matched_files = []
    for pattern in patterns:
        for root, dirs, files in os.walk(project_root):
            for file in files:
                if file.startswith(pattern):
                    matched_files.append(os.path.join(root, file))
    return matched_files

class CommandCompleter(Completer):
    def __init__(self, commands):
        self.commands = commands
        self.all_file_names = get_all_file_names_in_project()
        self.current_file_names = []

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = text.split()

        if len(words) > 0:
            if words[0] == "/add_files":
                current_word = words[-1]
                for file_name in self.all_file_names:
                    if file_name.startswith(current_word):
                        yield Completion(file_name, start_position=-len(current_word))
            elif words[0] == "/remove_files":
                current_word = words[-1]
                for file_name in self.current_file_names:
                    if file_name.startswith(current_word):
                        yield Completion(file_name, start_position=-len(current_word))
            else:
                for command in self.commands:
                    if command.startswith(text):
                        yield Completion(command, start_position=-len(text))
        else:
            for command in self.commands:
                if command.startswith(text):
                    yield Completion(command, start_position=-len(text))

    def update_current_files(self, files):
        self.current_file_names = [os.path.basename(f) for f in files]

completer = CommandCompleter(commands)

def save_memory():
    with open(os.path.join(".auto-coder-chat-lite", "memory.json"), "w") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def load_memory():
    global memory
    memory_path = os.path.join(".auto-coder-chat-lite", "memory.json")
    if os.path.exists(memory_path):
        with open(memory_path, "r") as f:
            memory = json.load(f)
    completer.update_current_files(memory["current_files"]["files"])

def add_files(args: List[str]):
    existing_files = memory["current_files"]["files"]
    matched_files = find_files_in_project(args)
    files_to_add = [f for f in matched_files if f not in existing_files]
    if files_to_add:
        memory["current_files"]["files"].extend(files_to_add)
        print(f"Added files: {files_to_add}")
    else:
        print("All specified files are already in the current session or no matches found.")
    completer.update_current_files(memory["current_files"]["files"])
    save_memory()

def remove_files(file_names: List[str]):
    removed_files = []
    for file in memory["current_files"]["files"]:
        if os.path.basename(file) in file_names:
            removed_files.append(file)
    for file in removed_files:
        memory["current_files"]["files"].remove(file)
    if removed_files:
        print(f"Removed files: {removed_files}")
    else:
        print("No files were removed.")
    completer.update_current_files(memory["current_files"]["files"])
    save_memory()

def list_files():
    current_files = memory["current_files"]["files"]
    if current_files:
        table = Table(title="Current Files")
        table.add_column("File", style="cyan")
        for file in current_files:
            table.add_row(os.path.basename(file))
        console = Console()
        console.print(table)
    else:
        print("No files in the current session.")

def show_help():
    print("Supported commands:")
    print("  /add_files <file1> <file2> ... - Add files to the current session")
    print("  /remove_files <file1> <file2> ... - Remove files from the current session")
    print("  /list_files - List all active files in the current session")
    print("  /coding <query> - Request the AI to modify code based on requirements")
    print("  /help - Show this help message")
    print("  /exit - Exit the program")

def main():
    load_memory()

    session = PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        enable_history_search=False,
        completer=completer,
        complete_while_typing=True,
    )

    print("Type /help to see available commands.\n")
    show_help()

    while True:
        try:
            user_input = session.prompt("> ")

            if user_input.startswith("/add_files"):
                args = user_input[len("/add_files") :].strip().split()
                add_files(args)
            elif user_input.startswith("/remove_files"):
                file_names = user_input[len("/remove_files") :].strip().split()
                remove_files(file_names)
            elif user_input.startswith("/list_files"):
                list_files()
            elif user_input.startswith("/coding"):
                query = user_input[len("/coding") :].strip()
                if not query:
                    print("Please enter your request.")
                else:
                    print("Coding request received:", query)
            elif user_input.startswith("/help"):
                show_help()
            elif user_input.startswith("/exit"):
                raise EOFError()
            else:
                print("Unknown command. Type /help to see available commands.")

        except KeyboardInterrupt:
            continue
        except EOFError:
            save_memory()
            print("\nExiting Chat Auto Coder...")
            break
        except Exception as e:
            print(f"An error occurred: {type(e).__name__} - {str(e)}")

if __name__ == "__main__":
    main()