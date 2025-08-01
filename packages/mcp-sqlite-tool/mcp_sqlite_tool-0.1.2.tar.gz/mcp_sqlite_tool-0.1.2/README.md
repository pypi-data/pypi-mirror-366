# MCP SQLite Tool

[![PyPI version](https://badge.fury.io/py/mcp-sqlite-tool.svg?icon=si%3Apython)](https://badge.fury.io/py/mcp-sqlite-tool) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An MCP server that provides AI with secure and direct access to SQLite databases.

## 🌟 Features

- **Secure Access:** Allows AI to interact with SQLite databases while validating file paths to prevent unauthorized access.
- **Single-File Server:** The core logic is contained in a single Python file, making it easy to understand and maintain.
- **Standard I/O (stdio) Transport:** Implements the official MCP protocol using standard I/O for seamless integration with tools like VS Code.
- **Pythonic & Easy to Use:** Built with the `fastmcp` framework, which uses decorators to simplify tool creation.

## 🚀 Installation

This tool is available as a package on PyPI. You can install it using `pip`.

```bash
pip install mcp-sqlite-tool
```

> **Note:** This tool requires Python 3.10 or higher. The `mcp[cli]` dependency will be installed automatically.

## 🤖 Usage with VS Code

To use this tool with an MCP-compatible client like VS Code, you need to configure your workspace to discover and run the server.

1. **Install the package:** Ensure you have the `mcp-sqlite-tool` package installed in the Python environment that VS Code is using.

    ```bash
    pip install mcp-sqlite-tool
    ```

2. **Configure `settings.json`:** Open the Command Palette in VS Code (`Ctrl+Shift+P`), search for "Open Workspace Settings (JSON)", and add the following configuration:

    ```json
    {
     "mcpServers": {
      "sqlite-query": {
       "command": "mcp-sqlite-tool"
      }
     }
    }
    ```

    - `"sqlite-query"`: This name identifies the server. It must match the name specified in the Python tool's code (`FastMCP("sqlite-query")`).
    - `"command": "mcp-sqlite-tool"`: This is the command-line entry point installed by `pip`. VS Code will use this to launch your server.

3. **Interact with the AI:** Once configured, the AI client will be able to use the tool `execute_sqlite_query`. You can now prompt the AI to interact with your SQLite files.

### Example Prompt

> "Using the `sqlite-query` tool, tell me the names and emails of all users in the `users` table of `C:\Users\John\Documents\project.db`."

The AI will interpret this request and call your tool with the appropriate arguments.

## 🛠️ Tool Documentation

The core tool provided by this server is:

### `execute_sqlite_query`

Executes a given SQL query on a specified SQLite database file.

| Parameter   | Type  | Description                                    |
| ----------- | ----- | ---------------------------------------------- |
| `db_path`   | `str` | The absolute path to the SQLite database file. |
| `sql_query` | `str` | The SQL query to execute.                      |

**Returns:** A dictionary containing the query results or an error message if the operation fails.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! If you have any issues, please contact me directly on [Telegram (@mrbeandev)](https://t.me/mrbeandev).

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
