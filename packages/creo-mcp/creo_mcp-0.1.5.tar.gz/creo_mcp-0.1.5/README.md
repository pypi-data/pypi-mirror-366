# Creo MCP

An MCP (Machine-Collaboration-Platform) server with tools for CAD interaction and knowledge base retrieval. This project exposes several functions as tools that a larger agent or system can call, including interacting with Creo and querying a Volcengine knowledge base.

---

## ⚙️ Key Features

* **CAD Integration**: Opens `.STEP` files directly in Creo Parametric.
* **Knowledge Base Retrieval**: Connects to and queries a Volcengine knowledge base.
* **Code Execution**: Provides a tool to execute arbitrary Python code remotely.
* **Command-Line Interface**: Runs as a standalone server application with configurable credentials.

---

## 📦 Installation & Setup

### Prerequisites

* Python 3.12 or newer
* **uv** package manager:
    * **On macOS:**
        ```bash
        brew install uv
        ```
    * **On Windows (PowerShell):**
        ```powershell
        powershell -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
        ```
        You may need to add `uv` to your Path manually:
        ```powershell
        # Add this line to your PowerShell profile
        $env:Path = "C:\Users\YOUR_USERNAME\.local\bin;" + $env:Path
        ```
    * For other systems, see the official [uv installation instructions](https://github.com/astral-sh/uv?tab=readme-ov-file#installation).

    ⚠️ **Do not proceed before installing uv.**

### Claude for Desktop Integration

1.  Go to `Claude > Settings > Developer > Edit Config > claude_desktop_config.json`.
2.  Add the following configuration to the `mcpServers` object:
    ```json
    {
        "mcpServers": {
            "creo_mcp": {
                "command": "uvx",
                "args": [
                    "creo-mcp",
                    "--authorization",
                    "YOUR_TOKEN_HERE",
                    "--service-resource-id",
                    "YOUR_ID_HERE"
                ]
            }
        }
    }
    ```
    *This allows Claude to automatically start your server when needed.*

### Cursor Integration

1.  Go to `Settings > MCP` in Cursor.
2.  Add a new server configuration.
    * **For macOS**: Use "add new global MCP server" or create a `.cursor/mcp.json` file in your project with the following content:
        ```json
        {
            "mcpServers": {
                "creo_mcp": {
                    "command": "uvx",
                    "args": [
                        "creo-mcp",
                        "--authorization",
                        "YOUR_TOKEN_HERE",
                        "--service-resource-id",
                        "YOUR_ID_HERE"
                    ]
                }
            }
        }
        ```
    * **For Windows**: Add a new server with the following settings:
        ```json
        {
            "mcpServers": {
                "creo_mcp": {
                    "command": "cmd",
                    "args": [
                        "/c",
                        "uvx",
                        "creo-mcp",
                        "--authorization",
                        "YOUR_TOKEN_HERE",
                        "--service-resource-id",
                        "YOUR_ID_HERE"
                    ]
                }
            }
        }
        ```

⚠️ **Only run one instance of the MCP server (either via Cursor or Claude Desktop), not both simultaneously.**

---

## ▶️ Manual Execution

If you need to run the server manually for debugging, first install it locally:

```bash
# Clone the repo
git clone [https://github.com/yangkunyi/creo-mcp.git](https://github.com/yangkunyi/creo-mcp.git)
cd creo-mcp

# Create a virtual environment and install in editable mode
uv venv
source .venv/bin/activate
uv pip install -e .
```

Then, run the server with your credentials:

```bash
creo-mcp --authorization YOUR_TOKEN_HERE --service-resource-id YOUR_ID_HERE
```

---

## 🛠️ Available Tools

The following tools are exposed by the server for remote execution:

* `execute_python_code`: Executes a given string of Python code.
* `open_file_in_cad`: Imports a `.STEP` file into Creo and opens it.
* `retrieve_from_knowledge_base`: Performs a retrieval query against the configured Volcengine knowledge base.
* `print_something`: Prints a given string to the server's console.
* `do_nothing`: A simple tool that does nothing.

---

## 🙏 Acknowledgements

The structure and setup instructions for this project were heavily inspired by the [blender-mcp](https://github.com/ahujasid/blender-mcp) project. Many thanks to its contributors for paving the way.

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.
