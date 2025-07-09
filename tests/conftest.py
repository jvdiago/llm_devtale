from pathlib import Path

import pytest
from llm_devtale.files import FileRepo


@pytest.fixture
def test_git_effort():
    return {"src/file1.py": 2, "src/file2.py": 1, "src/file3.py": 1}


@pytest.fixture
def test_repository(test_git_effort):
    return FileRepo(Path("."), test_git_effort)
