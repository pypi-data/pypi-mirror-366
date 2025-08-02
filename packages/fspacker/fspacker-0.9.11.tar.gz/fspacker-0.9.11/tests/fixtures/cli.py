import pytest
from typer.testing import CliRunner


@pytest.fixture
def typer_runner() -> CliRunner:
    """Typer CLI 测试工具.

    Returns:
        CliRunner 对象
    """
    return CliRunner()
