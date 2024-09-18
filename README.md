# auto-coder-chat-lite

[![PyPI](https://img.shields.io/pypi/v/auto-coder-chat-lite.svg)](https://pypi.org/project/auto-coder-chat-lite/)

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

After installation, you can run the tool using the following commands:

### `chat.code`

```bash
chat.code
```

This command starts the interactive command-line interface for code chat and project scaffolding. You can use the following commands within this interface:

- `/add_files <file1> <file2> ...` - Add files to the current session.
- `/remove_files <file1> <file2> ...` - Remove files from the current session.
- `/list_files` - List all active files in the current session.
- `/coding <query>` - Request the AI to modify code based on requirements.
- `/exclude_dirs <dir1> <dir2> ...` - Exclude directories from file searches.
- `/conf [<key> [<value>]]` - View or set configuration options.
- `/commit_message` - Generate a commit message based on Git diff.
- `/help` - Show this help message.
- `/exit` - Exit the program.

### `chat.agent`

```bash
chat.agent
```

This command is used to interact with the OpenAI API for chat completions. It requires the OpenAI API key and model configuration. You can set up the configuration using the following command:

```bash
chat.agent setup --api_key YOUR_API_KEY --base_url https://api.openai.com/v1 --model gpt-3.5-turbo
```

To test the configuration, you can use:

```bash
chat.agent test
```

### `chat.prompt`

```bash
chat.prompt
```

This command is used to render a template using Jinja2. It requires two arguments:

- `template_path`: Path to the template file.
- `text_path`: Path to the text file to be used as content.

Optionally, you can specify an output file path using the `-o` or `--output_path` flag (default is `output.txt`).

Example usage:

```bash
chat.prompt path/to/template.txt path/to/content.txt -o path/to/output.txt
```

This command will render the template with the provided content, save the result to the specified output file, and copy the rendered content to the clipboard.

## Dependencies

The project relies on the following Python packages:

- `colorama==0.4.6`
- `pathspec==0.12.1`
- `prompt_toolkit==3.0.47`
- `pydantic==2.8.2`
- `Pygments==2.18.0`
- `pyperclip==1.9.0`
- `rich==13.7.1`
- `GitPython==3.1.43`
- `Jinja2==3.1.4`
- `pylint==3.2.7`
- `openai==1.44.1`

These dependencies are automatically installed when you install `auto-coder-chat-lite` using pip.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue on the [GitHub repository](https://github.com/zt8989/auto-coder-chat-lite).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or feedback, please contact the author at [251027705@qq.com](mailto:251027705@qq.com).
