import os, subprocess

schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Executes a Python file",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Python file path to execute, relative to the working directory",
                },
                "args": {
                    "type": "array",
                    "description": "Arguments to pass to the Python file",
                    "items": {
                        "type": "string",
                    },
                },
            },
            "required": ["file_path"],
        },
    },
}

def run_python_file(
        working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    working_dir_abs = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(working_dir_abs, file_path))

    # Will be True or False
    valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs

    if not valid_target_dir:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_dir):
        return f'Error: "{file_path}" does not exist or is not a regular file'

    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file'

    absolute_file_path = os.path.abspath(target_dir)

    command = ["python", absolute_file_path]
    if args:
        command.extend(args)

    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True, cwd=working_dir_abs, timeout=30)
    except subprocess.CalledProcessError as e:
        return f'Error: executing Python file: {e}'

    if process.stdout is None and process.stderr is None:
        return f'No output produced'

    output = f'STDOUT: {process.stdout}' if process.stdout else ''
    error = f'STDERR: {process.stderr}' if process.stderr else ''
    returncodetext = ''

    if process.returncode != 0:
        returncodetext = f'Process exited with code {process.returncode}'

    return f'"{file_path}": ({output}{error})({returncodetext})'




