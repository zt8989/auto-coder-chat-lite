# 常量定义
PROJECT_DIR_NAME = ".auto-coder-chat-lite"

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
COMMAND_CD = "/cd"

MERGE_TYPE_SEARCH_REPLACE = "search_replace"
MERGE_TYPE_GIT_DIFF = "git_diff"

# Additional constants
SHOW_FILE_TREE = "show_file_tree"
EDITBLOCK_SIMILARITY = "editblock_similarity"
MERGE_TYPE = "merge_type"
MERGE_CONFIRM = "merge_confirm"

HUMAN_AS_MODEL = "human_as_model"

BOOLS = ["true", "false"]

CONF_AUTO_COMPLETE = {
    SHOW_FILE_TREE: BOOLS,
    MERGE_TYPE: [MERGE_TYPE_SEARCH_REPLACE, MERGE_TYPE_GIT_DIFF],
    MERGE_CONFIRM: BOOLS,
    HUMAN_AS_MODEL: BOOLS
}