from click.testing import CliRunner
from llm.cli import cli


def test_devtale_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["devtale", "--help"])
    assert result.exit_code == 0
    assert "Usage: cli devtale" in result.output
