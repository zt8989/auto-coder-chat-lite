import locale

# 获取系统语言设置
system_lang, _ = locale.getdefaultlocale()

# 定义语言字典
LANG = {
    'en': {
        'help_message': "\033[1mSupported commands:\033[0m",
        'add_files_help': "  \033[94m/add_files\033[0m \033[93m<file1> <file2> ...\033[0m - \033[92mAdd files to the current session\033[0m",
        'remove_files_help': "  \033[94m/remove_files\033[0m \033[93m<file1> <file2> ...\033[0m - \033[92mRemove files from the current session\033[0m",
        'list_files_help': "  \033[94m/list_files\033[0m - \033[92mList all active files in the current session\033[0m",
        'coding_help': "  \033[94m/coding\033[0m \033[93m<query>\033[0m - \033[92mRequest the AI to modify code based on requirements\033[0m",
        'commit_message_help': "  \033[94m/commit_message\033[0m [\033[93m<ref_id>\033[0m] - \033[92mGenerate a commit message based on git diff with optional ref_id\033[0m",
        'exit_help': "  \033[94m/exit\033[0m - \033[92mExit the program\033[0m",
        'files_added': "Added files: {}",
        'no_files_added': "All specified files are already in the current session, or no matches found, or excluded by .gitignore and exclude_dirs.",
        'files_removed': "Removed files: {}",
        'no_files_removed': "No files were removed.",
        'no_files': "No files in the current session.",
        'coding_request': "Please enter your request.",
        'coding_processed': "Coding request processed and output saved to output.txt.",
        'commit_message_generated': "Commit message generated and copied to clipboard. Also saved to output.txt.",
        'dirs_added': "Added exclude dirs: {}",
        'no_dirs_added': "All specified dirs are already in the exclude list.",
        'unknown_command': "Unknown command. Type /help to see available commands.",
        'exiting': "\nExiting Chat Auto Coder...",
        'error_occurred': "An error occurred: {} - {}",
        'type_help': "Type /help to see available commands.\n",
        'pyperclip_not_installed': "pyperclip not installed, unable to copy to clipboard.",
        'commit_message_saved': "Commit message saved to output.txt",
        'git_diff_error': "Error occurred while getting git diff",
        'git_diff_empty': "No changes detected in git diff",
        'verbose_help': "Enable verbose output mode",
        'template_not_exist': "Error: {} does not exist.",
        'merge_help': "  \033[94m/merge\033[0m - \033[92mMerge code changes\033[0m",
        'merge_started': "Starting code merge...",
        'merge_completed': "Code merge completed",
    },
    'zh': {
        'help_message': "\033[1m支持的命令：\033[0m",
        'add_files_help': "  \033[94m/add_files\033[0m \033[93m<文件1> <文件2> ...\033[0m - \033[92m将文件添加到当前会话\033[0m",
        'remove_files_help': "  \033[94m/remove_files\033[0m \033[93m<文件1> <文件2> ...\033[0m - \033[92m从当前会话中移除文件\033[0m",
        'list_files_help': "  \033[94m/list_files\033[0m - \033[92m列出当前会话中的所有活动文件\033[0m",
        'coding_help': "  \033[94m/coding\033[0m \033[93m<查询>\033[0m - \033[92m请求AI根据需求修改代码\033[0m",
        'commit_message_help': "  \033[94m/commit_message\033[0m [\033[93m<ref_id>\033[0m] - \033[92m根据git diff生成提交信息，可选ref_id\033[0m",
        'exit_help': "  \033[94m/exit\033[0m - \033[92m退出程序\033[0m",
        'files_added': "已添加文件：{}",
        'no_files_added': "所有指定的文件已在当前会话中，或未找到匹配项，或被.gitignore和exclude_dirs排除。",
        'files_removed': "已移除文件：{}",
        'no_files_removed': "没有文件被移除。",
        'no_files': "当前会话中没有文件。",
        'coding_request': "请输入您的请求。",
        'coding_processed': "代码请求已处理，输出已保存到output.txt。",
        'commit_message_generated': "提交信息已生成并复制到剪贴板。同时已保存到output.txt。",
        'dirs_added': "已添加排除目录：{}",
        'no_dirs_added': "所有指定的目录已在排除列表中。",
        'unknown_command': "未知命令。输入 /help 查看可用命令。",
        'exiting': "\n正在退出Chat Auto Coder...",
        'error_occurred': "发生错误：{} - {}",
        'type_help': "输入 /help 查看可用命令。\n",
        'pyperclip_not_installed': "未安装pyperclip,无法复制到剪贴板。",
        'commit_message_saved': "提交信息已保存到output.txt",
        'git_diff_error': "获取 git diff 时发生错误",
        'git_diff_empty': "git diff 未检测到任何更改",
        'verbose_help': "启用详细输出模式",
        'template_not_exist': "错误: {} 不存在。",
        'merge_help': "  \033[94m/merge\033[0m - \033[92m合并代码更改\033[0m",
        'merge_started': "开始合并代码...",
        'merge_completed': "代码合并完成",
    }
}

# 根据系统语言选择语言，默认为英语
CURRENT_LANG = 'zh' if system_lang and system_lang.startswith('zh') else 'en'

def get_text(key):
    return LANG[CURRENT_LANG].get(key, LANG['en'][key])