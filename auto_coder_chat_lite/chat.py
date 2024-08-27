import glob
import json
import os
import platform

if platform.system() == "Windows":
    from colorama import init
    init()

from typing import List
from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.completion import Completer, Completion
from rich.console import Console
from rich.table import Table
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from auto_coder_chat_lite.common import AutoCoderArgs
from auto_coder_chat_lite.common.code_auto_merge_editblock import CodeAutoMergeEditBlock

PROJECT_DIR_NAME = ".auto-coder-chat-lite"

memory = {
    "conversation": [],
    "current_files": {"files": [], "groups": {}},
    "conf": {"show_file_tree": False, "editblock_similarity": 0.8},
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
    "/conf",
]

def get_all_file_names_in_project() -> List[str]:
    project_root = os.getcwd()
    file_names = []
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in final_exclude_dirs]
        file_names.extend(files)
    return file_names


def get_all_file_in_project() -> List[str]:
    project_root = os.getcwd()
    file_names = []
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in final_exclude_dirs]
        for file in files:
            file_names.append(os.path.join(root, file))
    return file_names


def get_all_file_in_project_with_dot() -> List[str]:
    project_root = os.getcwd()
    file_names = []
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in final_exclude_dirs]
        for file in files:
            file_names.append(os.path.join(root, file).replace(project_root, "."))
    return file_names


def get_all_dir_names_in_project() -> List[str]:
    project_root = os.getcwd()
    dir_names = []
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in final_exclude_dirs]
        for dir in dirs:
            dir_names.append(dir)
    return dir_names


def get_all_file_names_in_project() -> List[str]:
    project_root = os.getcwd()
    file_names = []
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in final_exclude_dirs]
        file_names.extend(files)
    return file_names

def generate_file_tree(root_dir, indent_char='    ', last_char='', level_char=''):
    file_tree = []
    gitignore_path = os.path.join(root_dir, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
        spec = PathSpec.from_lines(GitWildMatchPattern, gitignore_content.splitlines())
    else:
        spec = PathSpec()

    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])

    def list_files(start_path, prefix=''):
        files = os.listdir(start_path)
        for i, file_name in enumerate(files):
            full_path = os.path.join(start_path, file_name)
            if spec.match_file(full_path) or any(exclude_dir in full_path for exclude_dir in final_exclude_dirs):
                continue
            is_last = i == len(files) - 1
            new_prefix = prefix + indent_char

            if os.path.isdir(full_path):
                file_tree.append(f"{new_prefix}{file_name}/")
                list_files(full_path, new_prefix)
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
        self.all_files = get_all_file_in_project()
        self.all_dir_names = get_all_dir_names_in_project()
        self.all_files_with_dot = get_all_file_in_project_with_dot()
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

    def refresh_files(self):
        self.all_file_names = get_all_file_names_in_project()
        self.all_files = get_all_file_in_project()
        self.all_dir_names = get_all_dir_names_in_project()
        self.all_files_with_dot = get_all_file_in_project_with_dot()
        # self.symbol_list = get_symbol_list()

completer = CommandCompleter(commands)

def save_memory():
    with open(os.path.join(PROJECT_DIR_NAME, "memory.json"), "w", encoding='utf-8') as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def load_memory():
    global memory
    memory_path = os.path.join(PROJECT_DIR_NAME, "memory.json")
    if os.path.exists(memory_path):
        with open(memory_path, "r", encoding='utf-8') as f:
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
    if "/all" in file_names:
        removed_files = memory["current_files"]["files"].copy()
        memory["current_files"]["files"] = []
    else:
        removed_files = []
        for pattern in file_names:
            matched_files = find_files_in_project([pattern])
            for file in matched_files:
                if file in memory["current_files"]["files"]:
                    removed_files.append(file)
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
            relative_path = os.path.relpath(file, os.getcwd())
            table.add_row(relative_path)
        console = Console()
        console.print(table)
    else:
        print("No files in the current session.")

def read_template():
    project_dir = os.path.join(os.getcwd(), PROJECT_DIR_NAME)
    template_path = os.path.join(project_dir, "template.txt")

    if os.path.exists(template_path):
        with open(template_path, "r", encoding='utf-8') as template_file:
            return template_file.read()
    else:    
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        template_path = os.path.join(current_dir, "template.txt")

        if not os.path.exists(template_path):
            print(f"Error: {template_path} does not exist.")
            return None

        with open(template_path, "r", encoding='utf-8') as template_file:
            return template_file.read()

def coding(query):
    project_root = os.getcwd()
    files = generate_file_tree(project_root)
    files_code = "\n".join(
        [f"##File: {file}\n{open(file, encoding='utf-8').read()}" for file in memory['current_files']['files'] if os.path.exists(file)]
    )

    template = read_template()
    files_to_pass = files if memory["conf"].get("show_file_tree", False) else ""
    replaced_template = template.format(
        project_root=project_root,
        files=files_to_pass,
        files_code=files_code,
        query=query
    )

    with open("output.txt", "w", encoding='utf-8') as output_file:
        output_file.write(replaced_template)

    try:
        import pyperclip
        pyperclip.copy(replaced_template)
    except ImportError:
        print("pyperclip not installed, unable to copy to clipboard.")

    print("Coding request processed and output saved to output.txt.")

    # 使用Console接收用户输入
    lines = []
    while True:
        line = prompt(FormattedText([("#00FF00", "> ")]), multiline=False)
        line_lower = line.strip().lower()
        if line_lower in ["eof", "/eof"]:
            break
        elif line_lower in ["/clear"]:
            lines = []
            print("\033[2J\033[H")  # Clear terminal screen
            continue
        elif line_lower in ["/break"]:
            raise Exception("User requested to break the operation.")
        lines.append(line)

    result = "\n".join(lines)

    editblock_similarity = memory["conf"].get("editblock_similarity", 0.8)
    args = AutoCoderArgs(file="output.txt", source_dir=project_root, editblock_similarity=editblock_similarity)
    code_auto_merge_editblock = CodeAutoMergeEditBlock(args)
    code_auto_merge_editblock.merge_code(result)

def exclude_dirs(dir_names: List[str]):
    new_dirs = dir_names
    existing_dirs = memory.get("exclude_dirs", [])
    dirs_to_add = [d for d in new_dirs if d not in existing_dirs]
    if dirs_to_add:
        existing_dirs.extend(dirs_to_add)
        if "exclude_dirs" not in memory:
            memory["exclude_dirs"] = existing_dirs
        print(f"Added exclude dirs: {dirs_to_add}")
    else:
        print("All specified dirs are already in the exclude list.")
    save_memory()
    completer.refresh_files()

def show_help():
    print("Supported commands:")
    print("  /add_files <file1> <file2> ... - Add files to the current session")
    print("  /remove_files <file1> <file2> ... - Remove files from the current session")
    print("  /list_files - List all active files in the current session")
    print("  /coding <query> - Request the AI to modify code based on requirements")
    print("  /help - Show this help message")
    print("  /exit - Exit the program")

def init_project():
    """
    初始化项目目录和内存文件。
    
    如果项目目录不存在，则创建该目录并初始化内存文件。
    """
    project_dir = PROJECT_DIR_NAME
    memory_file = os.path.join(project_dir, "memory.json")
    
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
        with open(memory_file, "w", encoding='utf-8') as f:
            json.dump({"current_files": {"files": []}, "conf": {}}, f, indent=2, ensure_ascii=False)
        print(f"Created directory {project_dir} and initialized {memory_file}")

    gitignore_path = os.path.join(os.getcwd(), ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w", encoding='utf-8') as f:
            f.write(f"{PROJECT_DIR_NAME}/\noutput.txt\n")
    else:
        with open(gitignore_path, "r", encoding='utf-8') as f:
            content = f.read()
        if f"{PROJECT_DIR_NAME}/" not in content:
            with open(gitignore_path, "a", encoding='utf-8') as f:
                f.write(f"{PROJECT_DIR_NAME}/\n")
        if "output.txt" not in content:
            with open(gitignore_path, "a", encoding='utf-8') as f:
                f.write("output.txt\n")

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
            elif user_input.startswith("/conf"):
                conf_args = user_input[len("/conf") :].strip().split()
                if len(conf_args) == 2:
                    key, value = conf_args
                    if key == "show_file_tree":
                        if value.lower() in ["true", "false"]:
                            memory["conf"][key] = value.lower() == "true"
                            print(f"Updated configuration: {key} = {memory['conf'][key]}")
                            save_memory()  # 更新配置值后调用 save_memory 方法
                        else:
                            print("Invalid value. Please provide 'true' or 'false'.")
                    elif key == "editblock_similarity":
                        try:
                            value = float(value)
                            if 0 <= value <= 1:
                                memory["conf"][key] = value
                                print(f"Updated configuration: {key} = {value}")
                                save_memory()  # 更新配置值后调用 save_memory 方法
                            else:
                                print("Invalid value. Please provide a number between 0 and 1.")
                        except ValueError:
                            print("Invalid value. Please provide a valid number.")
                    else:
                        try:
                            value = float(value)
                            memory["conf"][key] = value
                            print(f"Updated configuration: {key} = {value}")
                            save_memory()  # 更新配置值后调用 save_memory 方法
                        except ValueError:
                            print("Invalid value. Please provide a valid number.")
                elif len(conf_args) == 1:
                    key = conf_args[0]
                    if key in memory["conf"]:
                        print(f"Current configuration: {key} = {memory['conf'][key]}")
                    else:
                        print(f"Configuration key '{key}' not found.")
                elif len(conf_args) == 0:
                    if memory["conf"]:
                        print("Current configuration:")
                        for key, value in memory["conf"].items():
                            print(f"  {key} = {value}")
                    else:
                        print("No configuration values set.")
                else:
                    print("Usage: /conf [<key> [<value>]]")
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