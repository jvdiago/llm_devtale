from pathlib import Path

from llm_devtale.gitutils import GitRepository


class TestGitEffort:
    def test_get_commit_count(self, mocker):
        mocker.patch("llm_devtale.gitutils.Repo")
        git_stats = GitRepository(Path("."))
        mocker.patch.object(git_stats.repo.git, "rev_list", return_value="42")
        assert git_stats.get_commit_count() == 42

    def test_get_git_effort(self, mocker):
        mocker.patch("llm_devtale.gitutils.Repo")
        git_stats = GitRepository(Path("."))
        mocker.patch.object(
            git_stats.repo.git,
            "effort",
            return_value="file commits days\nsrc/file1.py..... 10 2\nsrc/file2.py..... 5 1",
        )
        assert git_stats.get_git_effort() == {"src/file1.py": 10, "src/file2.py": 5}

    def test_get_git_effort_bad_commit_count(self, mocker):
        mocker.patch("llm_devtale.gitutils.Repo")
        git_stats = GitRepository(Path("."))
        mocker.patch.object(
            git_stats.repo.git,
            "effort",
            return_value="src/file1.py..... dog 2\nsrc/file2.py..... 5 1",
        )
        assert git_stats.get_git_effort() == {"src/file1.py": 1, "src/file2.py": 5}
