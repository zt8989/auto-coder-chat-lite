(import os)
(import copy)

(setv PROJECT_DIR_NAME ".auto-coder-chat-lite")
(setv GITIGNORE_FILE ".gitignore")

(setv COMMAND_ADD_FILES "/add_files")
(setv COMMAND_REMOVE_FILES "/remove_files")
(setv COMMAND_LIST_FILES "/list_files")
(setv COMMAND_CODING "/coding")
(setv COMMAND_EXCLUDE_DIRS "/exclude_dirs")
(setv COMMAND_CONF "/conf")
(setv COMMAND_COMMIT_MESSAGE "/commit_message")
(setv COMMAND_HELP "/help")
(setv COMMAND_EXIT "/exit")
(setv COMMAND_MERGE "/merge")
(setv COMMAND_CD "/cd")

(setv MERGE_TYPE_SEARCH_REPLACE "search_replace")
(setv MERGE_TYPE_GIT_DIFF "git_diff")
(setv MERGE_TYPE_HYLANG "hylang")

(setv SHOW_FILE_TREE "show_file_tree")
(setv EDITBLOCK_SIMILARITY "editblock_similarity")
(setv MERGE_TYPE "merge_type")
(setv MERGE_CONFIRM "merge_confirm")

(setv LANGUAGE "language")

(setv HUMAN_AS_MODEL "human_as_model")

(setv BOOLS ["true" "false"])

(setv CONF_AUTO_COMPLETE
  {SHOW_FILE_TREE BOOLS
   MERGE_TYPE [MERGE_TYPE_SEARCH_REPLACE MERGE_TYPE_GIT_DIFF MERGE_TYPE_HYLANG]
   MERGE_CONFIRM BOOLS
   HUMAN_AS_MODEL BOOLS
   LANGUAGE ["zh" "en"]})

(setv defaut_exclude_dirs [".git/" "node_modules/" "dist/" "build/" "__pycache__/"])

(setv PROJECT_ROOT (os.getcwd))

(setv SOURCE_DIR (os.path.join (os.path.dirname (os.path.abspath __file__))))
(setv PROJECT_DIR (os.path.join PROJECT_ROOT PROJECT_DIR_NAME))
(setv TEMPLATES "template")

(setv _memory
  {"conversation" []
   "current_files" {"files" [] "groups" {}}
   "conf" {SHOW_FILE_TREE True EDITBLOCK_SIMILARITY 0.8 MERGE_TYPE MERGE_TYPE_SEARCH_REPLACE}
   "exclude_dirs" []
   "mode" "normal"})

(setv memory (copy.deepcopy _memory))