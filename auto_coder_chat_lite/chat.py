import copy
import glob
import json
import os
import platform
import traceback
import argparse
import git
import re
from jinja2 import Environment, FileSystemLoader

from typing import List
from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.table import Table
from rich.spinner import Spinner
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
import shutil

from auto_coder_chat_lite.lib.agent import external_chat_completion
from auto_coder_chat_lite.common import AutoCoderArgs
from auto_coder_chat_lite.common.code_auto_merge_editblock import CodeAutoMergeEditBlock
from auto_coder_chat_lite.common.git_diff_extractor import GitDiffExtractor
from auto_coder_chat_lite.lang import get_text
from auto_coder_chat_lite.common.config_manager import ConfigManager
from auto_coder_chat_lite.constants import (
    HUMAN_AS_MODEL,
    MERGE_CONFIRM,
    MERGE_TYPE,
    PROJECT_DIR_NAME,
    COMMAND_ADD_FILES,
    COMMAND_REMOVE_FILES,
    COMMAND_LIST_FILES,
    COMMAND_CODING,
    COMMAND_EXCLUDE_DIRS,
    COMMAND_CONF,
    COMMAND_COMMIT_MESSAGE,
    COMMAND_HELP,
    COMMAND_EXIT,
    COMMAND_MERGE,
    COMMAND_CD,
    MERGE_TYPE_SEARCH_REPLACE,
    MERGE_TYPE_GIT_DIFF,
    MERGE_TYPE_HYLANG,
    PROJECT_ROOT,
    defaut_exclude_dirs,
    memory,
    _memory,
    SHOW_FILE_TREE, 
    EDITBLOCK_SIMILARITY, 
    MERGE_TYPE, 
    MERGE_CONFIRM, 
    HUMAN_AS_MODEL
)
from auto_coder_chat_lite.lib.logger import setup_logger
from auto_coder_chat_lite.project import init_project
from auto_coder_chat_lite.configuration_handler import handle_configuration
from auto_coder_chat_lite.lib.merge import parse_and_eval_hylang

logger = setup_logger(__name__)

if platform.system() == "Windows":
    from colorama import init
    init()


# 在文件顶部添加常量定义
CURRENT_ROOT = PROJECT_ROOT  # 新增全局变量 CURRENT_ROOT，初始值等于 PROJECT_ROOT

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
    COMMAND_CD,  # 新增 /cd 命令
]

VERBOSE = False

def get_exclude_spec(root_dir: str = None):
    # 读取 .gitignore 文件
    gitignore_path = os.path.join(root_dir or PROJECT_ROOT, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
        spec = PathSpec.from_lines(GitWildMatchPattern, gitignore_content.splitlines())
    else:
        spec = PathSpec(patterns=[])
    
    # 获取排除目录
    final_exclude_dirs = defaut_exclude_dirs + memory.get("exclude_dirs", [])
    
    return spec, final_exclude_dirs



def generate_file_tree(root_dir, indent_char='    ', last_char='', level_char=''):
    file_tree = []
    spec, final_exclude_dirs = get_exclude_spec(root_dir)

    def list_files(start_path, prefix=''):
        files = sorted(os.listdir(start_path))
        for i, file_name in enumerate(files):
            full_path = os.path.join(start_path, file_name)
            if os.path.isdir(full_path):
                full_path = f"{full_path}/"
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

from auto_coder_chat_lite.command_completer import CommandCompleter
        # self.symbol_list = get_symbol_list()

completer = CommandCompleter(commands)

def save_memory():
    project_dir = os.path.join(CURRENT_ROOT, PROJECT_DIR_NAME)
    memory_file = os.path.join(project_dir, "memory.json")
    
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
    
    if not os.path.exists(memory_file):
        with open(memory_file, "w", encoding='utf-8') as f:
            json.dump({"current_files": {"files": []}, "conf": {}}, f, indent=2, ensure_ascii=False)
    
    config_manager = ConfigManager(memory_file)
    config_manager.save(memory)

def load_memory():
    project_dir = os.path.join(CURRENT_ROOT, PROJECT_DIR_NAME)
    memory_file = os.path.join(project_dir, "memory.json")
    
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
    
    if not os.path.exists(memory_file):
        with open(memory_file, "w", encoding='utf-8') as f:
            json.dump({"current_files": {"files": []}, "conf": {}}, f, indent=2, ensure_ascii=False)
    
    global memory
    config_manager = ConfigManager(memory_file)
    memory = config_manager.load(lambda: copy.deepcopy(_memory))
    if MERGE_TYPE not in memory["conf"]:
        memory["conf"][MERGE_TYPE] = MERGE_TYPE_SEARCH_REPLACE
    completer.update_current_files(memory["current_files"]["files"])

def get_files_to_add(args: List[str]):
    """
    Retrieves the list of files to be added based on the provided arguments.

    :param args: A list of file paths or patterns to be added.
    :return: A list of file paths that are to be added.
    """
    existing_files = memory["current_files"]["files"]
    matched_files = []
    
    for arg in args:
        if os.path.isabs(arg):  # 如果是绝对路径
            if os.path.exists(arg):  # 检查文件是否存在
                matched_files.append(arg)
        else:
            matched_files.extend(find_files_in_project([arg]))
    
    spec, final_exclude_dirs = get_exclude_spec()
    files_to_add = []
    for f in matched_files:
        if f not in existing_files:
            logger.info(f"File {f} not in existing files.")
        if not spec.match_file(f):
            logger.info(f"File {f} does not match spec.")
        if not any(exclude_dir in f for exclude_dir in final_exclude_dirs):
            logger.info(f"File {f} does not contain any exclude directories.")
        if f not in existing_files and not spec.match_file(f) and not any(exclude_dir in f for exclude_dir in final_exclude_dirs):
            files_to_add.append(f)
    return files_to_add

def add_files(args: List[str]):
    files_to_add = get_files_to_add(args)
    
    if files_to_add:
        memory["current_files"]["files"].extend(files_to_add)
        print(get_text('files_added').format(files_to_add))
    else:
        print(get_text('no_files_added'))
    
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
        print(get_text('files_removed').format(removed_files))
    else:
        print(get_text('no_files_removed'))
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
        print(get_text('no_files'))

def render_template(template_name, **kwargs):
    project_dir = os.path.join(PROJECT_ROOT, PROJECT_DIR_NAME)
    template_path_project = os.path.join(project_dir, "template")
    template_path_current = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template")

    if os.path.exists(os.path.join(template_path_project, template_name)):
        env = Environment(loader=FileSystemLoader(template_path_project))
    else:
        env = Environment(loader=FileSystemLoader(template_path_current))

    template = env.get_template(template_name)
    return template.render(**kwargs)

def get_user_input():
    """
    Collects user input until the user signals the end of input.
    
    The function prompts the user for input line by line. The user can signal the end of input by typing 'eof' or '/eof'.
    The user can also clear the current input by typing '/clear' or break the operation by typing '/break'.
    
    :return: A string containing all the lines of user input joined by newline characters.
    """
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
    """
    Merge the provided code result using the configured merge type.
    
    :param result: The code result to be merged.
    """
    if VERBOSE:
        logger.info(result)
    merge_type = memory["conf"].get(MERGE_TYPE, MERGE_TYPE_SEARCH_REPLACE)
    if merge_type == MERGE_TYPE_SEARCH_REPLACE:
        merge_code_search_replace(result)
    if merge_type == MERGE_TYPE_GIT_DIFF:
        git_diff_extractor = GitDiffExtractor(PROJECT_ROOT)
        diff_blocks = git_diff_extractor.extract_git_diff(result)
        if git_diff_extractor.apply_patch(diff_blocks):
            print("Git diff applied successfully.")
        else:
            print("Failed to apply git diff.")
    if merge_type == MERGE_TYPE_HYLANG:
        parse_and_eval_hylang(result)

def merge_code_search_replace(result: str):
    confirm = memory["conf"].get(MERGE_CONFIRM, False)
    editblock_similarity = memory["conf"].get("editblock_similarity", 0.8)
    args = AutoCoderArgs(file="output.txt", source_dir=PROJECT_ROOT, editblock_similarity=editblock_similarity)
    code_auto_merge_editblock = CodeAutoMergeEditBlock(args)
    code_auto_merge_editblock.merge_code(result, confirm=confirm)

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
        '.hy': 'hylang',  # Add support for .hy files
        # 添加更多文件类型
    }
    
    # 获取文件后缀
    file_extension = os.path.splitext(file_path)[1]
    
    # 判断文件类型
    file_type = known_file_types.get(file_extension, 'plaintext')
    
    return f"```{file_type}\n{file_code}\n```"
    
def coding(query: str):
    """
    Process the coding query and generate or prompt for code based on the provided context.

    :param query: The user's coding query.
    """
    files = generate_file_tree(CURRENT_ROOT)
    files_code = "\n".join(
        [f"##File: {file}\n{read_file(file)}" for file in memory['current_files']['files'] if os.path.exists(file)]
    )

    # Check if the query contains "@abc.fg" pattern
    file_pattern = re.compile(r'@(\w+\.\w+)')
    file_matches = file_pattern.findall(query)

    for file_match in file_matches:
        matched_files = get_files_to_add([file_match])
        for file_path in matched_files:
            if file_path not in memory['current_files']['files']:
                files_code += f"\n##File: {file_path}\n{read_file(file_path)}"

    try:
        import pyperclip
        clipboard_content = pyperclip.paste()
        query = query.format(clip=clipboard_content) if "{clip}" in query else query
    except ImportError:
        print(get_text('pyperclip_not_installed'))
    replaced_template = render_template("code.txt", files=files, project_root=CURRENT_ROOT, files_code=files_code, query=query, **memory['conf'])

    with open("output.txt", "w", encoding='utf-8') as output_file:
        output_file.write(replaced_template)

    if not memory["conf"].get("human_as_model", True):
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates code based on the provided context and query."},
            {"role": "user", "content": replaced_template}
        ]
        spinner = Spinner("dots", text="[cyan]Generating code...")
        result = ""

        terminal_height = shutil.get_terminal_size()[1]

        with Live(spinner, refresh_per_second=4) as live:
            response = external_chat_completion(messages, stream=True)
            if response:
                result = ""
                output = []
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        result += chunk.choices[0].delta.content
                        output = result.splitlines()
                        # Trim output_text to fit within terminal height
                        if len(output) > terminal_height - 4:
                            output_text = "\n".join(output[-terminal_height + 4:])
                        else:
                            output_text = result
                        live.update(
                            Panel(
                                Syntax(output_text, "markdown", theme="monokai"),
                                title="Generating Code",
                                border_style="green",
                            )
                        )
            else:
                logger.error("Failed to generate code.")
                return
    else:

        try:
            import pyperclip
            pyperclip.copy(replaced_template)
        except ImportError:
            print(get_text('pyperclip_not_installed'))

        print(get_text('coding_processed'))

        result = get_user_input()

    merge_code_with_editblock(result)

def merge_code():
    print(get_text('merge_started'))
    result = get_user_input()
    merge_code_with_editblock(result)
    print(get_text('merge_completed'))

def exclude_dirs(dir_names: List[str]):
    new_dirs = dir_names
    existing_dirs = memory.get("exclude_dirs", [])
    dirs_to_add = [d for d in new_dirs if d not in existing_dirs]
    if dirs_to_add:
        existing_dirs.extend(dirs_to_add)
        if "exclude_dirs" not in memory:
            memory["exclude_dirs"] = existing_dirs
        print(get_text('dirs_added').format(dirs_to_add))
    else:
        print(get_text('no_dirs_added'))
    save_memory()
    completer.refresh_files()

def show_help():
    print(get_text('help_message'))
    print(get_text('add_files_help'))
    print(get_text('remove_files_help'))
    print(get_text('list_files_help'))
    print(get_text('coding_help'))
    print(get_text('commit_message_help'))
    print(get_text('cd_help'))  # 新增 /cd 命令的帮助信息
    print(get_text('merge_help'))
    print(get_text('exit_help'))

def get_git_diff():
    repo = git.Repo(PROJECT_ROOT)
    try:
        diff_output = repo.git.diff(cached=True)
        if not diff_output:
            diff_output = repo.git.diff()
        
        if not diff_output:
            print(get_text('git_diff_empty'))
            return ""
        
        return diff_output
    except git.GitCommandError as e:
        print(get_text('git_diff_error'))
        return ""

def get_language():
    # 增加常用映射,比如 zh: 中文,en: English, 简称对应语言全称, 不存在则返回English
    language_map = {
        "zh": "中文",
        "en": "English",
        # 可以继续添加其他语言映射
    }

    # 首先读取 conf["language"] 的值
    language_code = memory["conf"].get("language")
    if language_code is None:
        # 如果 conf["language"] 为 None, 则根据当前环境判断 language
        import locale
        try:
            language_code = locale.getdefaultlocale()[0].split('_')[0]
        except:
            language_code = "en"  # 默认

    return language_map.get(language_code, "English")
    
def commit_message(ref_id=None):
    replaced_template = render_template("commit_message.txt", git_diff=get_git_diff(), language=get_language(), ref_id=ref_id)

    with open("output.txt", "w", encoding='utf-8') as output_file:
        output_file.write(replaced_template)

    if memory["conf"].get(HUMAN_AS_MODEL, True) == False:
        git_diff = get_git_diff()
        if not git_diff:
            print("No changes to commit.")
            return

        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates git commit messages."},
            {"role": "user", "content": replaced_template}
        ]

        spinner = Spinner("dots", text="[cyan]Generating commit message...")
        with Live(spinner, refresh_per_second=10):
            response = external_chat_completion(messages)
        if response:
            commit_message = response.choices[0].message.content.strip()
            # Remove triple backticks if present
            if commit_message.startswith("```") and commit_message.endswith("```"):
                commit_message = commit_message[3:-3].strip()
            console = Console()
            console.print(f"[bold green]Generated Commit Message:[/bold green]")
            for line in commit_message.splitlines():
                console.print(line)
            user_input = prompt("Do you want to commit with this message? (Y/n): ")
            if user_input.lower() != 'n':
                repo = git.Repo(PROJECT_ROOT)
                if not repo.index.diff("HEAD"):  # Check if there are staged files
                    repo.git.add(A=True)
                repo.index.commit(commit_message)
                print("Changes committed successfully.")
            else:
                print("Commit aborted by user.")
        else:
            logger.error("Failed to generate commit message.")
    else:
        try:
            import pyperclip
            pyperclip.copy(replaced_template)
            print(get_text('commit_message_generated'))
        except ImportError:
            print(get_text('pyperclip_not_installed'))

        print(get_text('commit_message_saved'))

def main():
    init_project()
    load_memory()

    kb = KeyBindings()

    @kb.add("c-n")
    def _(event):
        if HUMAN_AS_MODEL not in memory["conf"]:
            memory["conf"][HUMAN_AS_MODEL] = True

        current_status = memory["conf"][HUMAN_AS_MODEL]
        new_status = not current_status
        memory["conf"][HUMAN_AS_MODEL] = new_status
        save_memory()
        event.app.invalidate()

    def get_bottom_toolbar():
        human_as_model = memory["conf"].get(HUMAN_AS_MODEL, True)

        merge_confirm = memory["conf"].get(MERGE_CONFIRM, False)
        return (
            f" Model: {'human' if human_as_model else 'openai'} (ctl+n) | Merge Confirm: {'on' if merge_confirm else 'off'}"
        )

    session = PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        enable_history_search=False,
        completer=completer,
        complete_while_typing=True,
        key_bindings=kb,
        bottom_toolbar=get_bottom_toolbar
    )

    print("\033[1;34m" + get_text('type_help') + "\033[0m")
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
                ("class:host", "chat.code"),
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
                    print(get_text('coding_request'))
                else:
                    coding(query)
            elif user_input.startswith(COMMAND_EXCLUDE_DIRS):
                dir_names = user_input[len(COMMAND_EXCLUDE_DIRS):].strip().split()
                exclude_dirs(dir_names)
            elif user_input.startswith(COMMAND_CONF):
                handle_configuration(user_input, memory, save_memory)
            elif user_input.startswith(COMMAND_COMMIT_MESSAGE):
                ref_id = None
                if ' ' in user_input:
                    ref_id = user_input.split(' ')[1]
                commit_message(ref_id)
            elif user_input.startswith(COMMAND_HELP):
                show_help()
            elif user_input.startswith(COMMAND_EXIT):
                raise EOFError()
            elif user_input.startswith(COMMAND_MERGE):
                merge_code()
            elif user_input.startswith(COMMAND_CD):
                dir_name = user_input[len(COMMAND_CD):].strip()
                if os.path.isdir(dir_name):
                    global CURRENT_ROOT
                    CURRENT_ROOT = os.path.abspath(dir_name)
                    load_memory()
                    print(f"Changed directory to: {CURRENT_ROOT}")
                else:
                    print(f"Directory '{dir_name}' does not exist.")
            else:
                print(get_text('unknown_command'))

        except KeyboardInterrupt:
            continue
        except EOFError:
            save_memory()
            print(get_text('exiting'))
            break
        except Exception as e:
            if VERBOSE:
                logger.error(get_text('error_occurred').format(type(e).__name__, str(e)))
                logger.error(traceback.format_exc())
            else:
                logger.error(get_text('error_occurred').format(type(e).__name__, str(e)))

if __name__ == "__main__":
    VERBOSE = True
    main()