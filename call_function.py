from functions.get_files_info import schema_get_files_info, get_files_info
from functions.write_file import schema_write_file, write_file
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python_file import schema_run_python_file, run_python_file
import json
from inspect import signature
from collections.abc import Callable

function_map: dict[str, Callable[..., str]] = {
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
    "get_files_info": get_files_info,
}

available_functions = [
    schema_get_files_info,
    schema_write_file,
    schema_get_file_content,
    schema_run_python_file
]

def call_function(tool_call, verbose: bool = False) -> dict:
    function_name = tool_call.function.name

    def tool_result(content: str) -> dict:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": content,
        }

    if function_name not in function_map:
        return tool_result(f"Error: Unknown function: {function_name}")

    try:
        function_args = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError as error:
        return tool_result(f"Error: Invalid JSON arguments for {function_name}: {error}")

    if not isinstance(function_args, dict):
        return tool_result(f"Error: Arguments for {function_name} must be a JSON object")

    function_args["working_directory"] = "./calculator"

    if verbose:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    function = function_map[function_name]
    try:
        signature(function).bind(**function_args)
    except TypeError as error:
        return tool_result(f"Error: Invalid arguments for {function_name}: {error}")

    result = function(**function_args)

    return tool_result(result)
