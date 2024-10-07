import os
import copy
import json
from typing import List
from auto_coder_chat_lite.constants import (
    PROJECT_DIR_NAME,
    defaut_exclude_dirs,
    memory,
    PROJECT_ROOT,
    GITIGNORE_FILE
)
from auto_coder_chat_lite.lib.logger import setup_logger

logger = setup_logger(__name__)
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

    gitignore_path = os.path.join(os.getcwd(), GITIGNORE_FILE)
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w", encoding='utf-8') as f:
            f.write(f"{PROJECT_DIR_NAME}/\noutput.txt\n")
    else:
        with open(gitignore_path, "r", encoding='utf-8') as f:
            content = f.read()
        line_ending = "\n"
        if "\r\n" in content:
            line_ending = "\r\n"
        if not content.endswith(line_ending):
            content += line_ending
        if f"{PROJECT_DIR_NAME}/" not in content:
            content += f"{PROJECT_DIR_NAME}/{line_ending}"
        if "output.txt" not in content:
            content += f"output.txt{line_ending}"
        with open(gitignore_path, "w", encoding='utf-8') as f:
            f.write(content)

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