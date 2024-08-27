import locale

# 获取系统语言设置
system_lang, _ = locale.getdefaultlocale()

# 定义语言字典
LANG = {
    'en': {
        'help_message': "Supported commands:",
        'add_files_help': "  /add_files <file1> <file2> ... - Add files to the current session",
        'remove_files_help': "  /remove_files <file1> <file2> ... - Remove files from the current session",
        'list_files_help': "  /list_files - List all active files in the current session",
        'coding_help': "  /coding <query> - Request the AI to modify code based on requirements",
        'commit_message_help': "  /commit_message - Generate a commit message based on git diff",  # 新增这行
        'help_help': "  /help - Show this help message",
        'exit_help': "  /exit - Exit the program",
        'files_added': "Added files: {}",
        'no_files_added': "All specified files are already in the current session, or no matches found, or excluded by .gitignore and exclude_dirs.",
        'files_removed': "Removed files: {}",
        'no_files_removed': "No files were removed.",
        'no_files': "No files in the current session.",
        'coding_request': "Please enter your request.",
        'coding_processed': "Coding request processed and output saved to output.txt.",
        'commit_message_generated': "Commit message generated and copied to clipboard. Also saved to output.txt.",  # 新增这行
        'dirs_added': "Added exclude dirs: {}",
        'no_dirs_added': "All specified dirs are already in the exclude list.",
        'unknown_command': "Unknown command. Type /help to see available commands.",
        'exiting': "\nExiting Chat Auto Coder...",
        'error_occurred': "An error occurred: {} - {}",
        'type_help': "Type /help to see available commands.\n",
        'pyperclip_not_installed': "pyperclip not installed, unable to copy to clipboard.",
        'commit_message_saved': "Commit message saved to output.txt",
        'git_diff_error': "Error occurred while getting git diff",  # 新增这行
        'git_diff_empty': "No changes detected in git diff",
    },
    'zh': {
        'help_message': "支持的命令：",
        'add_files_help': "  /add_files <文件1> <文件2> ... - 将文件添加到当前会话",
        'remove_files_help': "  /remove_files <文件1> <文件2> ... - 从当前会话中移除文件",
        'list_files_help': "  /list_files - 列出当前会话中的所有活动文件",
        'coding_help': "  /coding <查询> - 请求AI根据需求修改代码",
        'commit_message_help': "  /commit_message - 根据git diff生成提交信息",  # 新增这行
        'help_help': "  /help - 显示此帮助信息",
        'exit_help': "  /exit - 退出程序",
        'files_added': "已添加文件：{}",
        'no_files_added': "所有指定的文件已在当前会话中，或未找到匹配项，或被.gitignore和exclude_dirs排除。",
        'files_removed': "已移除文件：{}",
        'no_files_removed': "没有文件被移除。",
        'no_files': "当前会话中没有文件。",
        'coding_request': "请输入您的请求。",
        'coding_processed': "代码请求已处理，输出已保存到output.txt。",
        'commit_message_generated': "提交信息已生成并复制到剪贴板。同时已保存到output.txt。",  # 新增这行
        'dirs_added': "已添加排除目录：{}",
        'no_dirs_added': "所有指定的目录已在排除列表中。",
        'unknown_command': "未知命令。输入 /help 查看可用命令。",
        'exiting': "\n正在退出Chat Auto Coder...",
        'error_occurred': "发生错误：{} - {}",
        'type_help': "输入 /help 查看可用命令。\n",
        'pyperclip_not_installed': "未安装pyperclip,无法复制到剪贴板。",
        'commit_message_saved': "提交信息已保存到output.txt",
        'git_diff_error': "获取 git diff 时发生错误",  # 新增这行
        'git_diff_empty': "git diff 未检测到任何更改",
    }
}

# 根据系统语言选择语言，默认为英语
CURRENT_LANG = 'zh' if system_lang and system_lang.startswith('zh') else 'en'

def get_text(key):
    return LANG[CURRENT_LANG].get(key, LANG['en'][key])