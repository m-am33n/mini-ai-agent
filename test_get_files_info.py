from functions.get_files_info import get_files_info

def test_get_files_info():
    print(get_files_info("calculator", "."))

    print(get_files_info("calculator", "pkg"))

    print(get_files_info("calculator", "/bin"))

    print(get_files_info("calculator", "../"))

    print(get_files_info("calculator", "main.py"))


if __name__ == "__main__":
    test_get_files_info()

