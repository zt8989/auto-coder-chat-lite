import glob
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
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

memory = {
    "conversation": [],
    "current_files": {"files": [], "groups": {}},
    "conf": {},
    "exclude_dirs": [],
    "mode": "normal",  # 新增mode字段,默认为normal模式
}

base_persist_dir = os.path.join(".auto-coder", "plugins", "chat-auto-coder")

defaut_exclude_dirs = [".git", "node_modules", "dist", "build", "__pycache__"]

commands = [
    "/add_files",
    "/remove_files",
    "/list_files",
    "/coding",
    "/help",
    "/exit",
    "/exclude_dirs",
]

def get_all_file_names_in_project() -> List[str]:
    project_root = os.getcwd()
    file_names = []
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in final_exclude_dirs]
        file_names.extend(files)
    return file_names

def generate_file_tree(root_dir, indent_char='|   ', last_char='|-- ', level_char='|-- '):
    file_tree = []
    gitignore_path = os.path.join(root_dir, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        spec = PathSpec.from_lines(GitWildMatchPattern, gitignore_content.splitlines())
    else:
        spec = PathSpec()

    def list_files(start_path, prefix=''):
        files = os.listdir(start_path)
        for i, file_name in enumerate(files):
            full_path = os.path.join(start_path, file_name)
            if spec.match_file(full_path):
                continue
            is_last = i == len(files) - 1
            if is_last:
                new_prefix = prefix + last_char
                next_prefix = prefix + indent_char + '   '
            else:
                new_prefix = prefix + level_char
                next_prefix = prefix + indent_char

            if os.path.isdir(full_path):
                file_tree.append(f"{new_prefix}{file_name}/")
                list_files(full_path, next_prefix)
            else:
                file_tree.append(f"{new_prefix}{file_name}")

    file_tree.append(f"{root_dir}/")
    list_files(root_dir)
    return "\n".join(file_tree)

def find_files_in_project(patterns: List[str]) -> List[str]:
    project_root = os.getcwd()
    matched_files = []
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])

    for pattern in patterns:
        if "*" in pattern or "?" in pattern:
            for file_path in glob.glob(pattern, recursive=True):
                if os.path.isfile(file_path):
                    abs_path = os.path.abspath(file_path)
                    if not any(
                        exclude_dir in abs_path.split(os.sep)
                        for exclude_dir in final_exclude_dirs
                    ):
                        matched_files.append(abs_path)
        else:
            is_added = False
            ## add files belongs to project
            for root, dirs, files in os.walk(project_root):
                dirs[:] = [d for d in dirs if d not in final_exclude_dirs]
                if pattern in files:
                    matched_files.append(os.path.join(root, pattern))
                    is_added = True
                else:
                    for file in files:
                        _pattern = os.path.abspath(pattern)
                        if _pattern in os.path.join(root, file):
                            matched_files.append(os.path.join(root, file))
                            is_added = True
            ## add files not belongs to project
            if not is_added:
                matched_files.append(pattern)

    return list(set(matched_files))



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
            elif words[0] == "/exclude_dirs":
                current_word = words[-1]
                for dir_name in self.all_dir_names:
                    if dir_name.startswith(current_word):
                        yield Completion(dir_name, start_position=-len(current_word))
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

def coding(query):
    project_root = os.getcwd()
    files = "\n".join(generate_file_tree(project_root))
    files_code = "\n".join(
        [f"##File: {file}\n{open(file).read()}" for file in memory['current_files']['files'] if os.path.exists(file)]
    )

    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    template_path = os.path.join(current_dir, "template.txt")

    if not os.path.exists(template_path):
        print(f"Error: {template_path} does not exist.")
        return

    with open(template_path, "r") as template_file:
        template = template_file.read()

    replaced_template = template.format(
        project_root=project_root,
        files=files,
        files_code=files_code,
        query=query
    )

    with open("output.txt", "w") as output_file:
        output_file.write(replaced_template)

    try:
        import pyperclip
        pyperclip.copy(replaced_template)
    except ImportError:
        print("pyperclip not installed, unable to copy to clipboard.")

    print("Coding request processed and output saved to output.txt.")

    # 使用Console接收用户输入
    console = Console()
    user_input = console.input("请输入要合并的代码块: ")

    # 调用merge_code方法
    from auto_coder_chat_lite.common.code_auto_merge_editblock import CodeAutoMergeEditBlock
    from auto_coder_chat_lite.common import AutoCoderArgs
    args = AutoCoderArgs(file="output.txt", source_dir=project_root, editblock_similarity=0.8)
    code_auto_merge_editblock = CodeAutoMergeEditBlock(args)
    code_auto_merge_editblock.merge_code(user_input)

def show_help():
    print("Supported commands:")
    print("  /add_files <file1> <file2> ... - Add files to the current session")
    print("  /remove_files <file1> <file2> ... - Remove files from the current session")
    print("  /list_files - List all active files in the current session")
    print("  /coding <query> - Request the AI to modify code based on requirements")
    print("  /help - Show this help message")
    print("  /exit - Exit the program")

def init_project():
    project_dir = ".auto-coder-chat-lite"
    memory_file = os.path.join(project_dir, "memory.json")
    
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
        with open(memory_file, "w") as f:
            json.dump({"current_files": {"files": []}, "conf": {}}, f, indent=2, ensure_ascii=False)
        print(f"Created directory {project_dir} and initialized {memory_file}")

def main():
    init_project()
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
                    coding(query)
            elif user_input.startswith("/exclude_dirs"):
                dir_names = user_input[len("/exclude_dirs") :].strip().split()
                exclude_dirs(dir_names)
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