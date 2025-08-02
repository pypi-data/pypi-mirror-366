import os
import shutil
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from fspacker.cli import app
from fspacker.settings import get_settings
from tests.conftest import DIR_ROOT


@pytest.fixture(autouse=True)
def enter_examples_dir(dir_examples: Path) -> None:
    os.chdir(dir_examples)


@pytest.fixture(autouse=True, scope="session")
def build_executable() -> None:
    """构建可执行文件, 在测试前执行."""
    os.chdir(DIR_ROOT)
    subprocess.run(["mkp", "dist"], check=True)


@pytest.fixture(autouse=True)
def clear_dist_folders(dir_ex00_simple: Path) -> None:
    """清理dist文件夹."""
    dist_dir = dir_ex00_simple / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir, ignore_errors=True)


@pytest.mark.slow
def test_build_command(typer_runner: CliRunner) -> None:
    """测试构建命令."""
    # Build normal
    result = typer_runner.invoke(app, ["b", "ex00"])
    assert result.exit_code == 0
    assert get_settings().mode.archive is False
    assert get_settings().mode.debug is False
    assert get_settings().mode.offline is False
    assert get_settings().mode.rebuild is False
    assert get_settings().mode.recursive is True
    assert get_settings().mode.simplify is True
    assert get_settings().mode.use_tk is False


@pytest.mark.slow
def test_build_command_archive_rebuild(typer_runner: CliRunner) -> None:
    """测试打包构建命令."""
    # Build with archive and rebuild
    result = typer_runner.invoke(app, ["b", "--archive", "--rebuild", "ex00"])
    assert result.exit_code == 0
    assert get_settings().mode.archive is True
    assert get_settings().mode.rebuild is True


@pytest.mark.slow
def test_build_command_invalid_match_name(
    typer_runner: CliRunner,
    dir_ex00_simple: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """测试匹配名称错误."""
    os.chdir(dir_ex00_simple)
    result = typer_runner.invoke(app, ["b", "invalid_match_name"])
    assert result.exit_code == 0
    assert "未找到匹配项目" in caplog.text


@pytest.mark.slow
def test_version_command(typer_runner: CliRunner, mocker: MagicMock) -> None:
    """测试版本命令."""
    mocker.patch("fspacker.__version__", "1.0.0")
    mocker.patch("fspacker.__build_date__", "2024-01-01")

    result = typer_runner.invoke(app, ["v"])
    assert "fspacker 1.0.0" in result.stdout
    assert "构建日期: 2024-01-01" in result.stdout
    assert result.exit_code == 0


@pytest.mark.slow
def test_clean_command(typer_runner: CliRunner, dir_ex00_simple: Path) -> None:
    """测试清理命令."""
    # Build
    result = typer_runner.invoke(app, ["b", "ex00"])
    assert result.exit_code == 0

    # Clean
    os.chdir(dir_ex00_simple)
    result = typer_runner.invoke(app, ["c"])
    assert not (dir_ex00_simple / "dist").exists()
