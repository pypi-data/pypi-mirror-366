import traceback
import creopyson
from mcp.server.fastmcp import FastMCP
import requests
import argparse  # Import the argparse library
import cq_gears
import cq_warehouse

mcp = FastMCP("python-code-executor")

# --- Global variables for credentials ---
# These will be set at runtime via command-line arguments.
AUTH_TOKEN = None
SERVICE_RESOURCE_ID = None


def get_creo_connection():
    c = creopyson.Client()
    c.connect()
    if not c.is_creo_running():
        raise Exception("Creo is not running")
    return c


@mcp.tool()
def execute_python_code(code: str) -> str:
    """
    Execute arbitrary Python code. Make sure to do it step-by-step by breaking it into smaller chunks.

    Parameters:
    - code: The Python code to execute

    Returns:
        A string containing the standard output of the executed code
        or an error message if the code fails.
    """
    # ctx.info(f"Attempting to execute the following code:\n---\n{code}\n---")

    # Use StringIO to create an in-memory text buffer to capture stdout
    try:
        # The 'with' statement ensures that stdout is restored even if errors occur
        exec(code)
        return "Code executed successfully"

    except Exception as e:
        # Capture the full traceback to return to the LLM for debugging
        # The traceback module provides more detail than just the exception message
        error_details = traceback.format_exc()
        return f"An error occurred:\n---\n{error_details}"


@mcp.tool()
def open_file_in_cad(file_path: str, name: str, dirname: str) -> str:
    """Opens a file in CAD software and returns the file path.

    Parameters:
    - file_path: The path to the file to open in CAD software.
    - name: The name to give the file in CAD software.
    - dirname: The absolute path to the directory which contains the file.

    Returns:
        The path to the file opened in CAD software.
    """
    try:
        c = get_creo_connection()
        path = c.interface_import_file(
            filename=file_path,
            file_type="STEP",
            new_name=name,
            new_model_type="prt",
            dirname=dirname,
        )
        c.file_open(path, display=True)
        return path
    except Exception as e:
        return f"An error occurred:\n---\n{e}"


KNOWLEDGE_BASE_DOMAIN = "api-knowledgebase.mlp.cn-beijing.volces.com"


@mcp.tool()
def retrieve_from_knowledge_base(
    query: str,
) -> str:
    """
    Performs a retrieval-type request from a Volcengine knowledge base service.
    This tool uses credentials (Authorization token and Service Resource ID)
    provided when the script was launched.

    Parameters:
    - query (str): The search query or question to retrieve relevant documents for.

    Returns:
    - str: A JSON string containing the list of retrieved results ('result_list') or an error message.
    """
    # --- 0. Check for Credentials ---
    if not AUTH_TOKEN or not SERVICE_RESOURCE_ID:
        return "Error: Authorization token and service resource ID were not provided at startup."

    try:
        # --- 1. Prepare Request Details ---
        api_path = "/api/knowledge/service/chat"
        request_url = f"http://{KNOWLEDGE_BASE_DOMAIN}{api_path}"

        # Set up the necessary headers, using the globally-set authorization token
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": f"Bearer {AUTH_TOKEN}",
        }

        # --- 2. Construct the Request Payload ---
        # Use the globally-set service resource ID
        payload = {
            "service_resource_id": SERVICE_RESOURCE_ID,
            "messages": [{"role": "user", "content": query}],
            "stream": False,  # Set to False for a single, complete retrieval response
        }

        # --- 3. Make the API Call ---
        response = requests.post(
            request_url,
            headers=headers,
            json=payload,
            timeout=30,  # Set a reasonable timeout for the request
        )

        # Check for HTTP errors (e.g., 401 Unauthorized, 404 Not Found)
        response.raise_for_status()

        # Ensure the response is decoded correctly
        response.encoding = "utf-8"

        # Return the raw JSON response as a string
        return response.text

    except requests.exceptions.RequestException as e:
        # Handle network-related errors and bad HTTP status codes
        error_body = e.response.text if e.response else "No response body"
        return f"An HTTP error occurred: {e}\nResponse: {error_body}"
    except Exception:
        # Handle any other unexpected errors and provide a detailed traceback
        error_details = traceback.format_exc()
        return f"An unexpected error occurred:\n---\n{error_details}"


@mcp.prompt()
def model_creation_strategy() -> str:
    """Define the strategy for creating models in Creo."""
    return """
## Core Directives
**Validate Before Generating**: Before writing any code, you must first validate the user's request for logical, geometrical, and parametric feasibility.

- **Geometrically/Logically Impossible**: Reject prompts that are impossible by definition (e.g., "Make a cube with five sides," "Draw a two-dimensional sphere").
- **Parametrically Invalid**: Reject prompts that use invalid parameters (e.g., "Create a block with a negative length," "Make a cylinder with a radius of zero").

**Correction and Guidance**: If a request is invalid, you must not attempt to generate code. Instead, you must respond to the user by:
1. Politely stating the problem.
2. Clearly explaining why the request is invalid.
3. Suggesting a valid alternative or asking for the specific information needed to proceed.

**Adhere to Workflow**: For all valid requests, you must strictly follow the workflow defined below.

## Available Tools
You must operate using only the specific tools defined in the script.
- `retrieve_from_knowledge_base(query: str)`: Use this tool to get accurate information about the CadQuery, cq_gears, and cq_warehouse libraries. If you are unsure about a function, class, or its parameters, you must use this tool to verify it.
- `execute_python_code(code: str)`: Use this tool to run the Python code you generate. The code must be passed as a single string.
- `open_file_in_cad(file_path: str, name: str, dirname: str)`: Use this tool to open the generated STEP file in the CAD software (Creo).

You must not use any other tools for writing or saving files.

## Workflow
You must follow these steps in sequence for every valid user request:

1.  **Analyze the Request**: Carefully understand the user's geometric requirements, applying the validation checks outlined in the Core Directives. If the request is valid, proceed.
2.  **Consult Knowledge Base (If Necessary)**: If the request involves complex or unfamiliar features, use the `retrieve_from_knowledge_base` tool to find the correct CadQuery functions and syntax.
3.  **Generate Python Code String**: Write a complete Python script as a single string. This script must:
    - Import the cadquery library (e.g., `import cadquery as cq`).
    - Contain the logic to build the 3D model.
    - Save the final model to a file in STEP format. The filename, including the `.step` extension, must be unique, descriptive, and no longer than 10 characters. For example, `cq.exporters.export(result, 'spur_gear_24t_module1.step')`.
4.  **Execute the Code**: Pass the entire Python code string to the `execute_python_code` tool.
5.  **Handle Execution Errors**: If the `execute_python_code` tool returns an error, you must print the complete error message to aid in debugging before attempting to fix the code.
6.  **Open the File in CAD**: After the code is executed successfully, call the `open_file_in_cad` tool. You must provide the correct `file_path` (e.g., 'spur_gear_24t_module1.step'), a `name` for the model in the CAD software, and the `dirname` where the file was saved. Try to use a simple and short name.
"""


def main():
    parser = argparse.ArgumentParser(
        description="Run the MCP server with credentials for the knowledge base."
    )
    parser.add_argument(
        "--authorization",
        type=str,
        required=True,
        help="The authorization token (bearer token) for the knowledge base API.",
    )
    parser.add_argument(
        "--service-resource-id",
        type=str,
        required=True,
        help="The service resource ID for the knowledge base.",
    )
    args = parser.parse_args()

    # --- 2. Set Global Credentials from Arguments ---
    # We use 'global' to modify the variables defined at the top of the script
    global AUTH_TOKEN, SERVICE_RESOURCE_ID
    AUTH_TOKEN = args.authorization
    SERVICE_RESOURCE_ID = args.service_resource_id

    # --- 3. Start the Server ---
    print("Starting MCP server with provided credentials...")
    mcp.run()


if __name__ == "__main__":
    main()
