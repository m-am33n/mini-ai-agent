from functions.get_file_content import get_file_content

def test_get_file_content():
    test_cases = [
        ("calculator", "lorem.txt"),
        ("calculator", "main.py"),
        ("calculator", "pkg/calculator.py"),
        ("calculator", "/bin/cat"),
        ("calculator", "pkg/does_not_exist.py"),
    ]

    for working_directory, file_path in test_cases:
        result = get_file_content(working_directory, file_path)
        if result.startswith("Error: "):
            print(result)
            continue
        print(f"{file_path} length: {len(result)}")
        print(f"{file_path} truncated: {'truncated' in result}")
        if file_path != "lorem.txt":
            print(result)

if __name__ == "__main__":
    test_get_file_content()
