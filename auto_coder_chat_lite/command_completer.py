import os
from prompt_toolkit.completion import Completer, Completion
from auto_coder_chat_lite.common.command_completer import CommandTextParser
from auto_coder_chat_lite.project import get_all_file_names_in_project, get_all_file_in_project, get_all_dir_names_in_project, get_all_file_in_project_with_dot
from auto_coder_chat_lite.constants import (
    CONF_AUTO_COMPLETE,
    COMMAND_ADD_FILES,
    COMMAND_REMOVE_FILES,
    COMMAND_CODING,
    COMMAND_EXCLUDE_DIRS,
    COMMAND_CONF,
    COMMAND_CD,
)

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
            elif words[0] == COMMAND_CD:
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
            elif words[0] == COMMAND_CONF:
                current_word = words[-1]
                if len(words) == 1 and text[-1] == ' ':
                    for key in CONF_AUTO_COMPLETE:
                        yield Completion(key, start_position=0)
                elif len(words) == 2 and text[-1] == ' ':
                    key = words[1]
                    if key in CONF_AUTO_COMPLETE:
                        for sub_key in CONF_AUTO_COMPLETE[key]:
                            yield Completion(sub_key, start_position=0)
                elif len(words) == 2:
                    for key in CONF_AUTO_COMPLETE:
                        if key.startswith(current_word):
                            yield Completion(key, start_position=-len(current_word))
                elif len(words) == 3:
                    key = words[1]
                    if key in CONF_AUTO_COMPLETE:
                        for value in CONF_AUTO_COMPLETE[key]:
                            if value.startswith(current_word):
                                yield Completion(value, start_position=-len(current_word))
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