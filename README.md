# Mini AI Agent

A small Python coding agent that turns a command-line prompt into file operations
and Python execution. It uses OpenRouter through the OpenAI Python client and
works on the included calculator project: it can inspect code, make changes, and
run tests using four callable tools.

## How it works

1. You supply a task as a command-line argument.
2. The agent sends the task, its system prompt, and tool definitions to the model.
3. When the model requests a tool, the dispatcher validates the arguments and
   runs the corresponding Python function against `./calculator`.
4. Tool results are added to the conversation so the model can choose its next
   action. A run makes at most 20 model requests and ends early when the model
   stops requesting tools.

Each invocation starts a new conversation; chat history is kept in memory only.

## Setup

You need Python 3.13 or newer, `uv`, and an OpenRouter API key.

```bash
git clone https://github.com/m-am33n/mini-ai-agent.git
cd mini-ai-agent
uv sync --locked
```

Create a `.env` file in the repository root:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
```

You can also set `OPENROUTER_API_KEY` in your shell environment. The `.env` file
is excluded from Git.

## Usage

Run commands from the repository root. Paths in prompts are relative to the
`calculator/` directory, so `main.py` in a prompt refers to the calculator's
entry point.

```bash
# Explore the calculator project
uv run main.py "List the files in the working directory"

# Read a specific file
uv run main.py "Read pkg/calculator.py and explain how operator precedence works"

# Execute the calculator through the agent
uv run main.py "Run main.py with the argument '3 + 5 * 2'"

# Ask for a code change and verification
uv run main.py "Add support for parentheses in calculator expressions, add tests, and run tests.py"

# Show tool arguments, full tool results, and token usage when reported
uv run main.py "Run tests.py" --verbose
```

The agent executes requested tools automatically, including file writes. Model
responses and the sequence of tool calls can vary between runs.

## Available tools

| Tool | Purpose | Behavior |
| --- | --- | --- |
| `get_files_info` | List directory entries | Reports file sizes and whether each entry is a directory; defaults to `.`. |
| `get_file_content` | Read a text file | Returns up to 10,000 characters, with a notice if the file is truncated. |
| `write_file` | Create or overwrite a file | Creates missing parent directories and replaces existing file contents. |
| `run_python_file` | Execute a Python file | Accepts optional arguments, captures output, and applies a 30-second timeout. |

The dispatcher injects `./calculator` as the working directory, overriding any
model-supplied value. Unknown tools, malformed JSON, and missing or unexpected
arguments are returned as tool errors.

## Try the calculator without the agent

The calculator can run locally without an API key or a model request:

```bash
uv run calculator/main.py "3 + 5 * 2"
```

```json
{
  "expression": "3 + 5 * 2",
  "result": 13
}
```

It currently supports `+`, `-`, `*`, and `/` with operator precedence. Separate
numbers and operators with spaces. Parentheses are not currently supported.

## Tests

Run the assertion-based tests without calling the model or using an API key:

```bash
# Tool dispatch and argument validation
uv run python -m unittest test_call_function -v

# Calculator behavior
uv run python calculator/tests.py -v
```

The other root-level `test_*.py` files are manual smoke-test scripts that print
tool results. Run them individually, for example:

```bash
uv run python test_get_files_info.py
uv run python test_get_file_content.py
uv run python test_run_python_file.py
```

`test_write_file.py` overwrites `calculator/lorem.txt` and
`calculator/pkg/morelorem.txt` when run.

## Project layout

```text
main.py                  CLI, model requests, and agent loop
prompts.py               System instructions for the agent
call_function.py         Tool registry, argument validation, and dispatch
functions/               File listing, reading, writing, and Python execution
calculator/              Sample project the agent operates on
test_call_function.py    Dispatcher unit tests
test_*.py                Individual tool smoke tests
pyproject.toml           Python version and dependencies
uv.lock                  Locked dependency versions
```

## Configuration and limitations

- **Model:** `main.py` currently uses `openrouter/free` at
  `https://openrouter.ai/api/v1`. Change the model string there to use another
  compatible model. There is no model-selection CLI flag.
- **Workspace:** `call_function.py` fixes the tool working directory to
  `./calculator`. Change that value to work on another project, and adjust the
  calculator-specific instructions in `prompts.py`.
- **Execution:** This is a learning project with direct local execution. Path
  checks reject ordinary paths outside the workspace, but do not resolve
  symlinks. Executed Python inherits the host's permissions and environment, so
  the workspace checks are not a security sandbox. Use a disposable environment
  for untrusted code.
- **Data and edits:** Prompts and tool results, including file contents, are sent
  to the model provider. File changes have no approval step or automatic rollback;
  use Git to review them.
- **Error handling:** Some failures, including API errors, file I/O errors, and
  execution timeouts, can terminate a run. Automatic retries are not implemented.
