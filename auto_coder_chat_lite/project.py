import os
import json
from auto_coder_chat_lite.constants import PROJECT_DIR_NAME
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