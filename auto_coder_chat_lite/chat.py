import glob
import json
import os
import platform
import subprocess
import traceback
import argparse
import logging
import git

# 设置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

if platform.system() == "Windows":
    from colorama import init
    init()

from typing import List
from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.completion import Completer, Completion
from rich.console import Console
from rich.table import Table
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from auto_coder_chat_lite.common import AutoCoderArgs
from auto_coder_chat_lite.common.code_auto_merge_editblock import CodeAutoMergeEditBlock
from auto_coder_chat_lite.common.command_completer import CommandTextParser
from auto_coder_chat_lite.lang import get_text

PROJECT_DIR_NAME = ".auto-coder-chat-lite"

memory = {
    "conversation": [],
    "current_files": {"files": [], "groups": {}},
    "conf": {"show_file_tree": False, "editblock_similarity": 0.8},
    "exclude_dirs": [],
    "mode": "normal",  # 新增mode字段,默认为normal模式
}

defaut_exclude_dirs = [".git", "node_modules", "dist", "build", "__pycache__"]

# 在文件顶部添加常量定义
PROJECT_ROOT = os.getcwd()

# 在文件顶部添加以下常量定义
COMMAND_ADD_FILES = "/add_files"
COMMAND_REMOVE_FILES = "/remove_files"
COMMAND_LIST_FILES = "/list_files"
COMMAND_CODING = "/coding"
COMMAND_EXCLUDE_DIRS = "/exclude_dirs"
COMMAND_CONF = "/conf"
COMMAND_COMMIT_MESSAGE = "/commit_message"
COMMAND_HELP = "/help"
COMMAND_EXIT = "/exit"
COMMAND_MERGE = "/merge"

# 更新commands列表
commands = [
    COMMAND_ADD_FILES,
    COMMAND_REMOVE_FILES,
    COMMAND_LIST_FILES,
    COMMAND_CODING,
    COMMAND_HELP,
    COMMAND_EXIT,
    COMMAND_EXCLUDE_DIRS,
    COMMAND_CONF,
    COMMAND_COMMIT_MESSAGE,
    COMMAND_MERGE,
]

def get_exclude_spec():
    # 读取 .gitignore 文件
    gitignore_path = os.path.join(PROJECT_ROOT, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
        spec = PathSpec.from_lines(GitWildMatchPattern, gitignore_content.splitlines())
    else:
        spec = PathSpec()
    
    # 获取排除目录
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])
    
    return spec, final_exclude_dirs

def get_all_file_names_in_project() -> List[str]:
    file_names = []
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in final_exclude_dirs]
        file_names.extend(files)
    return file_names

def get_all_file_in_project() -> List[str]:
    file_names = []
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in final_exclude_dirs]
        for file in files:
            file_names.append(os.path.join(root, file))
    return file_names

def get_all_file_in_project_with_dot() -> List[str]:
    file_names = []
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in final_exclude_dirs]
        for file in files:
            file_names.append(os.path.join(root, file).replace(PROJECT_ROOT, "."))
    return file_names

def get_all_dir_names_in_project() -> List[str]:
    dir_names = []
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in final_exclude_dirs]
        for dir in dirs:
            dir_names.append(dir)
    return dir_names

def generate_file_tree(root_dir, indent_char='    ', last_char='', level_char=''):
    file_tree = []
    spec, final_exclude_dirs = get_exclude_spec()

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
    matched_files = []
    spec, final_exclude_dirs = get_exclude_spec()

    for pattern in patterns:
        if "*" in pattern or "?" in pattern:
            for file_path in glob.glob(pattern, recursive=True):
                if os.path.isfile(file_path):
                    abs_path = os.path.abspath(file_path)
                    if not spec.match_file(abs_path) and not any(
                        exclude_dir in abs_path.split(os.sep)
                        for exclude_dir in final_exclude_dirs
                    ):
                        matched_files.append(abs_path)
        else:
            is_added = False
            ## add files belongs to project
            for root, dirs, files in os.walk(PROJECT_ROOT):
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
            if words[0] == COMMAND_ADD_FILES:
                current_word = words[-1]
                for file_name in self.all_file_names:
                    if file_name.startswith(current_word):
                        yield Completion(file_name, start_position=-len(current_word))
            elif words[0] == COMMAND_REMOVE_FILES:
                current_word = words[-1]
                for file_name in self.current_file_names:
                    if file_name.startswith(current_word):
                        yield Completion(file_name, start_position=-len(current_word))
            elif words[0] == COMMAND_EXCLUDE_DIRS:
                current_word = words[-1]
                for dir_name in self.all_dir_names:
                    if dir_name.startswith(current_word):
                        yield Completion(dir_name, start_position=-len(current_word))
            elif words[0] == COMMAND_CODING:
                new_text = text[len(words[0]) :]
                parser = CommandTextParser(new_text, words[0])
                parser.coding()
                current_word = parser.current_word()

                all_tags = parser.tags

                if current_word.startswith("@"):
                    name = current_word[1:]
                    target_set = set()

                    for file_name in self.current_file_names:
                        base_file_name = os.path.basename(file_name)
                        if name in base_file_name:
                            target_set.add(base_file_name)
                            path_parts = file_name.split(os.sep)
                            display_name = (
                                os.sep.join(path_parts[-3:])
                                if len(path_parts) > 3
                                else file_name
                            )
                            yield Completion(
                                base_file_name,
                                start_position=-len(name),
                                display=f"{display_name} (in active files)",
                            )

                    for file_name in self.all_file_names:
                        if file_name.startswith(name) and file_name not in target_set:
                            target_set.add(file_name)
                            yield Completion(file_name, start_position=-len(name))

                    for file_name in self.all_files:
                        if name in file_name and file_name not in target_set:
                            yield Completion(file_name, start_position=-len(name))
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
    
    spec, final_exclude_dirs = get_exclude_spec()
    
    # 过滤文件
    files_to_add = []
    for f in matched_files:
        if f not in existing_files and not spec.match_file(f) and not any(exclude_dir in f for exclude_dir in final_exclude_dirs):
            files_to_add.append(f)
    
    if files_to_add:
        memory["current_files"]["files"].extend(files_to_add)
        logger.info(get_text('files_added').format(files_to_add))
    else:
        logger.info(get_text('no_files_added'))
    
    completer.update_current_files(memory["current_files"]["files"])
    save_memory()

def remove_files(file_names: List[str]):
    if "/all" in file_names:
        removed_files = memory["current_files"]["files"].copy()
        memory["current_files"]["files"] = []
    elif "/clean" in file_names:
        removed_files = [file for file in memory["current_files"]["files"] if not os.path.exists(file)]
        for file in removed_files:
            memory["current_files"]["files"].remove(file)
    else:
        removed_files = []
        for pattern in file_names:
            matched_files = find_files_in_project([pattern])
            for file in matched_files:
                if file in memory["current_files"]["files"]:
                    removed_files.append(file)
                    memory["current_files"]["files"].remove(file)
    if removed_files:
        logger.info(get_text('files_removed').format(removed_files))
    else:
        logger.info(get_text('no_files_removed'))
    completer.update_current_files(memory["current_files"]["files"])
    save_memory()
    
def list_files():
    current_files = memory["current_files"]["files"]
    if current_files:
        table = Table(title="Current Files")
        table.add_column("File", style="cyan")
        for file in current_files:
            relative_path = os.path.relpath(file, PROJECT_ROOT)
            table.add_row(relative_path)
        console = Console()
        console.print(table)
    else:
        logger.info(get_text('no_files'))

def read_template(template_name):
    project_dir = os.path.join(PROJECT_ROOT, PROJECT_DIR_NAME)
    template_path = os.path.join(project_dir, "template", template_name)

    if os.path.exists(template_path):
        with open(template_path, "r", encoding='utf-8') as template_file:
            return template_file.read()
    else:    
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        template_path = os.path.join(current_dir, "template", template_name)

        if not os.path.exists(template_path):
            logger.error(get_text('template_not_exist').format(template_path))
            return None

        with open(template_path, "r", encoding='utf-8') as template_file:
            return template_file.read()

def get_user_input():
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
    return "\n".join(lines)

def merge_code_with_editblock(result: str):
    editblock_similarity = memory["conf"].get("editblock_similarity", 0.8)
    args = AutoCoderArgs(file="output.txt", source_dir=PROJECT_ROOT, editblock_similarity=editblock_similarity)
    code_auto_merge_editblock = CodeAutoMergeEditBlock(args)
    code_auto_merge_editblock.merge_code(result)

def read_file(file_path):
    with open(file_path, encoding='utf-8') as f:
        file_code = f.read()
    
    # 已知文件类型列表
    known_file_types = {
        '.py': 'python',
        '.js': 'javascript',
        '.html': 'html',
        '.css': 'css',
        '.md': 'markdown',
        '.json': 'json',
        '.txt': 'plaintext',
        # 添加更多文件类型
    }
    
    # 获取文件后缀
    file_extension = os.path.splitext(file_path)[1]
    
    # 判断文件类型
    file_type = known_file_types.get(file_extension, 'plaintext')
    
    return f"```{file_type}\n{file_code}\n```"
    
def coding(query):
    files = generate_file_tree(PROJECT_ROOT)
    files_code = "\n".join(
        [f"##File: {file}\n{read_file(file)}" for file in memory['current_files']['files'] if os.path.exists(file)]
    )

    template = read_template("code.txt")
    files_to_pass = files if memory["conf"].get("show_file_tree", False) else ""
    replaced_template = template.format(
        project_root=PROJECT_ROOT,
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
        logger.info(get_text('pyperclip_not_installed'))

    logger.info(get_text('coding_processed'))

    result = get_user_input()
    merge_code_with_editblock(result)

def merge_code():
    logger.info(get_text('merge_started'))
    result = get_user_input()
    merge_code_with_editblock(result)
    logger.info(get_text('merge_completed'))

def exclude_dirs(dir_names: List[str]):
    new_dirs = dir_names
    existing_dirs = memory.get("exclude_dirs", [])
    dirs_to_add = [d for d in new_dirs if d not in existing_dirs]
    if dirs_to_add:
        existing_dirs.extend(dirs_to_add)
        if "exclude_dirs" not in memory:
            memory["exclude_dirs"] = existing_dirs
        logger.info(get_text('dirs_added').format(dirs_to_add))
    else:
        logger.info(get_text('no_dirs_added'))
    save_memory()
    completer.refresh_files()

def show_help():
    logger.info(get_text('help_message'))
    logger.info(get_text('add_files_help'))
    logger.info(get_text('remove_files_help'))
    logger.info(get_text('list_files_help'))
    logger.info(get_text('coding_help'))
    logger.info(get_text('commit_message_help'))
    logger.info(get_text('merge_help'))
    logger.info(get_text('exit_help'))

def init_project():
    """
    Initialize project directory and memory file.
    
    If the project directory doesn't exist, create it and initialize the memory file.
    """
    project_dir = PROJECT_DIR_NAME
    memory_file = os.path.join(project_dir, "memory.json")
    
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
        with open(memory_file, "w", encoding='utf-8') as f:
            json.dump({"current_files": {"files": []}, "conf": {}}, f, indent=2, ensure_ascii=False)
        logger.info(f"Created directory {project_dir} and initialized {memory_file}")

    gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
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

def get_git_diff():
    repo = git.Repo(PROJECT_ROOT)
    try:
        diff_output = repo.git.diff(cached=True)
        if not diff_output:
            diff_output = repo.git.diff()
        
        if not diff_output:
            logger.info(get_text('git_diff_empty'))
            return ""
        
        return diff_output
    except git.GitCommandError as e:
        logger.info(get_text('git_diff_error'))
        return ""

def commit_message():
    template = read_template("commit_message.txt")
    if template is None:
        return

    git_diff = get_git_diff()
    
    # 根据当前环境判断 language
    import locale
    try:
        language = locale.getdefaultlocale()[0].split('_')[0]
    except:
        language = "en"  # 默认语言为英语
    
    replaced_template = template.format(
        git_diff=git_diff,
        language=language
    )

    with open("output.txt", "w", encoding='utf-8') as output_file:
        output_file.write(replaced_template)

    try:
        import pyperclip
        pyperclip.copy(replaced_template)
        logger.info(get_text('commit_message_generated'))
    except ImportError:
        logger.info(get_text('pyperclip_not_installed'))

    logger.info(get_text('commit_message_saved'))

def main(verbose=False):
    init_project()
    load_memory()

    session = PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        enable_history_search=False,
        completer=completer,
        complete_while_typing=True,
    )

    logger.info("\033[1;34m" + get_text('type_help') + "\033[0m")
    show_help()

    style = Style.from_dict(
        {
            "username": "#884444",
            "at": "#00aa00",
            "colon": "#0000aa",
            "pound": "#00aa00",
            "host": "#00ffff bg:#444400",
        }
    )

    while True:
        try:
            prompt_message = [
                ("class:username", "coding"),
                ("class:at", "@"),
                ("class:host", "code.chat"),
                ("class:colon", ":"),
                ("class:path", "~"),
                ("class:dollar", "$ "),
            ]
            user_input = session.prompt(FormattedText(prompt_message), style=style)

            if user_input.startswith(COMMAND_ADD_FILES):
                args = user_input[len(COMMAND_ADD_FILES):].strip().split()
                add_files(args)
            elif user_input.startswith(COMMAND_REMOVE_FILES):
                file_names = user_input[len(COMMAND_REMOVE_FILES):].strip().split()
                remove_files(file_names)
            elif user_input.startswith(COMMAND_LIST_FILES):
                list_files()
            elif user_input.startswith(COMMAND_CODING):
                query = user_input[len(COMMAND_CODING):].strip()
                if not query:
                    logger.info(get_text('coding_request'))
                else:
                    coding(query)
            elif user_input.startswith(COMMAND_EXCLUDE_DIRS):
                dir_names = user_input[len(COMMAND_EXCLUDE_DIRS):].strip().split()
                exclude_dirs(dir_names)
            elif user_input.startswith(COMMAND_CONF):
                conf_args = user_input[len(COMMAND_CONF):].strip().split()
                if len(conf_args) == 2:
                    key, value = conf_args
                    if key == "show_file_tree":
                        if value.lower() in ["true", "false"]:
                            memory["conf"][key] = value.lower() == "true"
                            logger.info(f"Updated configuration: {key} = {memory['conf'][key]}")
                            save_memory()  # 更新配置值后调用 save_memory 方法
                        else:
                            logger.info("Invalid value. Please provide 'true' or 'false'.")
                    elif key == "editblock_similarity":
                        try:
                            value = float(value)
                            if 0 <= value <= 1:
                                memory["conf"][key] = value
                                logger.info(f"Updated configuration: {key} = {value}")
                                save_memory()  # 更新配置值后调用 save_memory 方法
                            else:
                                logger.info("Invalid value. Please provide a number between 0 and 1.")
                        except ValueError:
                            logger.info("Invalid value. Please provide a valid number.")
                    else:
                        try:
                            value = float(value)
                            memory["conf"][key] = value
                            logger.info(f"Updated configuration: {key} = {value}")
                            save_memory()  # 更新配置值后调用 save_memory 方法
                        except ValueError:
                            logger.info("Invalid value. Please provide a valid number.")
                elif len(conf_args) == 1:
                    key = conf_args[0]
                    if key in memory["conf"]:
                        logger.info(f"Current configuration: {key} = {memory['conf'][key]}")
                    else:
                        logger.info(f"Configuration key '{key}' not found.")
                elif len(conf_args) == 0:
                    if memory["conf"]:
                        logger.info("Current configuration:")
                        for key, value in memory["conf"].items():
                            logger.info(f"  {key} = {value}")
                    else:
                        logger.info("No configuration values set.")
                else:
                    logger.info("Usage: /conf [<key> [<value>]]")
            elif user_input.startswith(COMMAND_COMMIT_MESSAGE):
                commit_message()
            elif user_input.startswith(COMMAND_HELP):
                show_help()
            elif user_input.startswith(COMMAND_EXIT):
                raise EOFError()
            elif user_input.startswith(COMMAND_MERGE):
                merge_code()
            else:
                logger.info(get_text('unknown_command'))

        except KeyboardInterrupt:
            continue
        except EOFError:
            save_memory()
            logger.info(get_text('exiting'))
            break
        except Exception as e:
            if verbose:
                logger.error(get_text('error_occurred').format(type(e).__name__, str(e)))
                logger.error(traceback.format_exc())
            else:
                logger.error(get_text('error_occurred').format(type(e).__name__, str(e)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto Coder Chat Lite")
    parser.add_argument("-v", "--verbose", action="store_true", help=get_text('verbose_help'))
    args = parser.parse_args()
    
    main(verbose=args.verbose)