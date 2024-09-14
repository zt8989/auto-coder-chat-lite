# auto-coder-chat-lite

[![PyPI](https://img.shields.io/pypi/v/auto-coder-chat-lite.svg)](https://pypi.org/project/auto-coder-chat-lite/)

一个轻量级的AI代码生成工具。

[English](./README.md) | [中文](./readme-cn.md)

## 概述

`auto-coder-chat-lite` 是一个轻量级工具，旨在促进代码聊天和项目脚手架。它提供了一个命令行界面，允许用户添加、删除和列出文件，以及请求基于AI的代码修改。

## 安装

要安装 `auto-coder-chat-lite`，你需要安装 Python 3.6 或更高版本。然后，你可以使用 pip 安装该包：

```bash
pip install auto-coder-chat-lite
```

## 使用

安装后，你可以使用以下命令运行工具：

### `chat.code`

```bash
chat.code
```

此命令启动用于代码聊天和项目脚手架的交互式命令行界面。你可以在该界面中使用以下命令：

- `/add_files <file1> <file2> ...` - 添加文件到当前会话。
- `/remove_files <file1> <file2> ...` - 从当前会话中删除文件。
- `/list_files` - 列出当前会话中的所有活动文件。
- `/coding <query>` - 根据需求请求AI修改代码。
- `/exclude_dirs <dir1> <dir2> ...` - 从文件搜索中排除目录。
- `/conf [<key> [<value>]]` - 查看或设置配置选项。
- `/commit_message` - 根据Git差异生成提交消息。
- `/help` - 显示帮助信息。
- `/exit` - 退出程序。

### `chat.prompt`

```bash
chat.prompt
```

此命令用于使用 Jinja2 渲染模板。它需要两个参数：

- `template_path`: 模板文件的路径。
- `text_path`: 作为内容使用的文本文件的路径。

你还可以使用 `-o` 或 `--output_path` 标志指定输出文件路径（默认是 `output.txt`）。

示例用法：

```bash
chat.prompt path/to/template.txt path/to/content.txt -o path/to/output.txt
```

此命令将使用提供的文本内容渲染模板，将结果保存到指定的输出文件，并将渲染后的内容复制到剪贴板。

## 依赖

该项目依赖于以下 Python 包：

- `colorama==0.4.6`
- `loguru==0.7.2`
- `markdown-it-py==3.0.0`
- `mdurl==0.1.2`
- `pathspec==0.12.1`
- `prompt_toolkit==3.0.47`
- `pydantic==2.8.2`
- `pydantic_core==2.20.1`
- `Pygments==2.18.0`
- `pyperclip==1.9.0`
- `rich==13.7.1`
- `wcwidth==0.2.13`
- `GitPython==3.1.43`
- `Jinja2==3.1.4`
- `openai==1.44.1`

这些依赖在安装 `auto-coder-chat-lite` 时会自动安装。

## 贡献

欢迎贡献！请随时提交拉取请求或在 [GitHub 仓库](https://github.com/zt8989/auto-coder-chat-lite) 上打开问题。

## 许可证

本项目采用 MIT 许可证。有关更多详细信息，请参见 [LICENSE](LICENSE) 文件。

## 联系

如有任何问题或反馈，请联系作者 [251027705@qq.com](mailto:251027705@qq.com)。