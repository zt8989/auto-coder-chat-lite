# auto-coder-chat-lite

A lightweight AI code generation tool.

[English](./README.md) | [中文](./readme-cn.md)

## Overview

`auto-coder-chat-lite` is a lightweight tool designed to facilitate code chat and project scaffolding. It provides a command-line interface for interacting with the project, allowing users to add, remove, and list files, as well as request AI-based code modifications.

## Installation

To install `auto-coder-chat-lite`, you need to have Python 3.6 or higher installed. Then, you can install the package using pip:

```bash
pip install auto-coder-chat-lite
```

## Usage

After installation, you can run the tool using the following command:

```bash
code.chat
```

This will start the interactive command-line interface where you can use the following commands:

- `/add_files <file1> <file2> ...` - Add files to the current session.
- `/remove_files <file1> <file2> ...` - Remove files from the current session.
- `/list_files` - List all active files in the current session.
- `/coding <query>` - Request the AI to modify code based on requirements.
- `/exclude_dirs <dir1> <dir2> ...` - Exclude directories from file searches.
- `/conf [<key> [<value>]]` - View or set configuration options.
- `/commit_message` - Generate a commit message based on Git diff.
- `/help` - Show this help message.
- `/exit` - Exit the program.

## Dependencies

The project relies on the following Python packages:

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

These dependencies are automatically installed when you install `auto-coder-chat-lite` using pip.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue on the [GitHub repository](https://github.com/zt8989/auto-coder-chat-lite).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or feedback, please contact the author at [251027705@qq.com](mailto:251027705@qq.com).
