import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from call_function import call_function, function_map


def tool_call(arguments, name="write_file"):
    return SimpleNamespace(
        id="test-call",
        function=SimpleNamespace(name=name, arguments=arguments),
    )


class CallFunctionTests(unittest.TestCase):
    def assert_tool_error(self, result, message):
        self.assertEqual(result["role"], "tool")
        self.assertEqual(result["tool_call_id"], "test-call")
        self.assertTrue(result["content"].startswith("Error:"))
        self.assertIn(message, result["content"])

    def test_missing_content_returns_error_without_opening_file(self):
        with patch("builtins.open") as open_file:
            result = call_function(tool_call('{"file_path": "test_bug_case.py"}'))
        self.assert_tool_error(result, "content")
        open_file.assert_not_called()

    def test_malformed_json_returns_error(self):
        result = call_function(tool_call('{"file_path":'))
        self.assert_tool_error(result, "Invalid JSON")

    def test_non_object_arguments_return_error(self):
        for arguments in ("null", "[]", '"text"', "42"):
            with self.subTest(arguments=arguments):
                self.assert_tool_error(
                    call_function(tool_call(arguments)), "JSON object"
                )

    def test_unexpected_argument_returns_error(self):
        result = call_function(tool_call(json.dumps({
            "file_path": "test_bug_case.py", "content": "", "extra": True,
        })))
        self.assert_tool_error(result, "extra")

    def test_corrected_call_executes_and_accepts_empty_content(self):
        writes = []

        def write_file(working_directory, file_path, content):
            writes.append((working_directory, file_path, content))
            return "written"

        with patch.dict(function_map, {"write_file": write_file}):
            self.assert_tool_error(
                call_function(tool_call('{"file_path": "test_bug_case.py"}')),
                "content",
            )
            self.assertEqual(writes, [])
            result = call_function(tool_call(json.dumps({
                "file_path": "test_bug_case.py", "content": "",
                "working_directory": "/tmp",
            })))
        self.assertEqual(writes, [("./calculator", "test_bug_case.py", "")])
        self.assertEqual(result, {
            "role": "tool", "tool_call_id": "test-call", "content": "written",
        })

    def test_optional_arguments_keep_defaults(self):
        def get_files_info(working_directory, directory="."):
            return f"{working_directory}:{directory}"

        with patch.dict(function_map, {"get_files_info": get_files_info}):
            result = call_function(tool_call("{}", name="get_files_info"))
        self.assertEqual(result["content"], "./calculator:.")

    def test_unknown_function_returns_error(self):
        self.assert_tool_error(
            call_function(tool_call("{}", name="unknown")), "Unknown function"
        )


if __name__ == "__main__":
    unittest.main()
