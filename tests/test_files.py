
from llm_devtale.files import FileRepo, FileSelector


class TestGetFilesByToken:
    def test_get_files_by_token(self, mocker, test_repository):
        file_selector = FileSelector(test_repository)
        file_selector.allowed_extensions = [".py"]
        mocker.patch("builtins.open")
        mocker.patch("llm_devtale.files.TokenCounter.count_tokens", return_value=100)

        token_count = 0
        hot_files, total_token_count = file_selector.get_files_by_token(token_count)
        assert hot_files == []
        assert total_token_count == 0

        token_count = 100
        hot_files, total_token_count = file_selector.get_files_by_token(token_count)
        assert hot_files == ["src/file1.py"]
        assert total_token_count == 100

        token_count = 1000
        hot_files, total_token_count = file_selector.get_files_by_token(token_count)
        assert hot_files == ["src/file1.py", "src/file2.py", "src/file3.py"]
        assert total_token_count == 300

    def test_get_files_by_token_0_tokens(self, mocker, test_repository):
        file_selector = FileSelector(test_repository)
        file_selector.allowed_extensions = [".py"]
        mocker.patch("builtins.open")
        mocker.patch("llm_devtale.files.FileSelector.count_tokens", return_value=0)
        token_count = 10000
        hot_files, total_token_count = file_selector.get_files_by_token(token_count)
        assert hot_files == []
        assert total_token_count == 0

    def test_get_files_by_token_file_too_large(self, mocker, test_repository):
        file_selector = FileSelector(test_repository)
        file_selector.allowed_extensions = [".py"]

        max_tokens_per_file = 20000

        mocker.patch("builtins.open")
        mocker.patch(
            "llm_devtale.files.TokenCounter.count_tokens",
            side_effect=[
                100,
                max_tokens_per_file + 1,
                100,
            ],
        )

        token_count = 10000000
        hot_files, total_token_count = file_selector.get_files_by_token(
            token_count, max_tokens_per_file
        )
        assert hot_files == ["src/file1.py", "src/file3.py"]
        assert total_token_count == 200


def test_valid_extension(test_repository: FileRepo):
    file_selector = FileSelector(test_repository)
    file_selector.allowed_extensions = [".py", ".txt"]

    # Test case 1: Valid extension
    file = "file.py"
    assert file_selector.valid_extension(file) is True

    # Test case 2: Invalid extension
    file = "file.js"
    assert file_selector.valid_extension(file) is False


def test_valid_file(mocker, test_repository: FileRepo):
    file_selector = FileSelector(test_repository)
    file_selector.allowed_extensions = [".py"]
    file_selector.ignore_patterns = ["tests"]
    mocker.patch("os.path.isfile", return_value=True)

    # Test case 1: Valid file
    file = "src/file.py"
    assert file_selector.valid_file(file) is True

    # Test case 2: Invalid file extension
    file = "src/file.js"
    assert file_selector.valid_file(file) is False

    # Test case 3: Ignored file pattern
    file = "tests/test_file.py"
    assert file_selector.valid_file(file) is False

    # Test case 4: Ignored parent directory pattern
    file = "src/tests/test_file.py"
    assert file_selector.valid_file(file) is False

    # Test case 5: Invalid file with no code extension
    file = "src/file"
    assert file_selector.valid_file(file) is False
