from .gitutils import GitRepository
from .files import FileSelector, FileRepo
from .config import ParserConfig
from .parser import ProjectParser
from .node import Node
from pathlib import Path


def main():
    repo_path = Path("/home/vela/git/llm-devtale")
    config = ParserConfig(
        directory=repo_path, model_name="gemini/gemini-2.5-flash-preview-04-17"
    )
    git_repo: GitRepository = GitRepository(repo_path)
    effort: dict[str, int] = git_repo.get_git_effort()
    file_repo: FileRepo = FileRepo(repo_path, effort)
    file_selector = FileSelector(
        file_repo,
        ignore_patterns=config.ignore_patterns,
        allowed_extensions=config.allowed_extensions,
    )
    valid_files, token_count = file_selector.get_files_by_token(
        max_token_count=config.max_tokens_per_project,
        max_tokens_per_file=config.max_tokens_per_file,
    )
    project_parser: ProjectParser = ProjectParser(
        parser_config=config, valid_files=valid_files
    )
    node: Node = project_parser.parse()
    print("Token count:", token_count)
    node.print()


if __name__ == "__main__":
    main()
