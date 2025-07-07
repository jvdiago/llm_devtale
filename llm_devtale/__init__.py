from pathlib import Path

import click
import llm

from .config import ParserConfig
from .files import FileRepo, FileSelector
from .gitutils import GitRepository
from .node import Node
from .parser import ProjectParser


@llm.hookimpl
def register_commands(cli):
    @cli.command(name="devtale", help="Create documentation from source files")
    @click.argument(
        "directory",
        type=click.Path(exists=True, file_okay=False, dir_okay=True),
        default=".",
    )
    @click.option(
        "--exclude", "-e", multiple=True, help="Patterns to exclude (gitignore format)"
    )
    @click.option(
        "--max-tokens", type=int, help="Maximum number of tokens to send to the LLM"
    )
    @click.option(
        "--max-tokens-per-file",
        type=int,
        help="Max tokens per file",
    )
    @click.option(
        "--output", "-o", type=click.Path(), help="Output file path or directory"
    )
    @click.option("--model", "-m", help="LLM model to use")
    @click.option(
        "--filter-extension",
        "-f",
        multiple=True,
        help="Only include files with these extensions",
    )
    def devtale(
        directory,
        exclude,
        max_tokens,
        max_tokens_per_file,
        output,
        model,
        filter_extension,
    ):
        try:
            config = ParserConfig(
                directory=directory,
                model_name=model,
                max_tokens_per_file=max_tokens_per_file,
                max_tokens_per_project=max_tokens,
                exclude_patterns=exclude,
                allowed_extensions=filter_extension,
            )
            git_repo: GitRepository = GitRepository(directory)
            effort: dict[str, int] = git_repo.get_git_effort()
            file_repo: FileRepo = FileRepo(directory, effort)
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
            print("File Token count:", token_count)
            result = node.to_string()

            # Save or display the output
            if output:
                output_file = Path(output)

                with open(output_file, "w") as f:
                    f.write(result)

            # Print the output if JSON format or explicitly requested
            else:
                click.echo(result)
        except Exception as e:
            click.echo(f"[bold red]Error: {e}")
            raise click.Abort()
