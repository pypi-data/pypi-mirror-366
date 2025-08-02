from __future__ import annotations

from pathlib import Path

import pytest

from fspacker.exceptions import ProjectParseError
from fspacker.parsers.project import Project


@pytest.mark.parametrize(
    ("dirname", "dependencies"),
    [
        ("ex01_helloworld", ["tomli>=2.2.1", "xlrd>=2.0.1"]),
        ("ex02_office", ["pypdf>=5.4.0"]),
        ("ex03_tkinter", ["pyyaml>=6.0.2"]),
        ("ex04_pyside2", ["pyside2>=5.15.2.1"]),
        ("ex11_pygame", ["pygame>=2.6.1"]),
    ],
)
def test_project(
    dir_examples: Path,
    dirname: str,
    dependencies: list[str],
) -> None:
    info = Project(dir_examples / dirname)
    assert info.name == dirname.replace("_", "-")
    assert str(info) == f"[green bold]{info.name}[/]"
    assert info.dependencies == dependencies
    assert info.dist_dir == dir_examples / dirname / "dist"
    assert info.runtime_dir == dir_examples / dirname / "dist" / "runtime"
    assert info.exe_file == dir_examples / dirname / "dist" / f"{dirname}.exe"


def test_project_poetry(dir_ex09_poetry_py310: Path) -> None:
    info = Project(dir_ex09_poetry_py310)
    assert info.name == "ex09-poetry-py310"
    assert info.dependencies == [
        "pygame<2.7.0,>=2.6.1",
        "tomli<3.0.0,>=2.2.1",
        "typer>=0.15.2",
    ]
    assert info.python_specifiers == ">=3.10,<4.0"


@pytest.mark.parametrize(
    ("dirname", "is_gui"),
    [
        ("ex01_helloworld", False),
        ("ex02_office", False),
        ("ex03_tkinter", True),
        ("ex04_pyside2", True),
        ("ex09_poetry_py310", True),
        ("ex11_pygame", True),
    ],
)
def test_project_is_gui(
    dir_examples: Path,
    dirname: str,
    *,
    is_gui: bool,
) -> None:
    info = Project(dir_examples / dirname)
    assert info.is_gui == is_gui


def test_project_error_invalid_project_dir() -> None:
    """测试解析无效的项目目录."""
    with pytest.raises(ProjectParseError) as execinfo:
        Project(None)
    assert "项目路径无效: None" in str(execinfo.value)

    with pytest.raises(ProjectParseError) as execinfo:
        Project(Path("nonexistent_dir"))
    assert "项目路径无效: nonexistent_dir" in str(execinfo.value)


def test_project_error_invalid_project_file(
    dir_ex90_error_no_project: Path,
) -> None:
    """测试解析无效的项目文件."""
    with pytest.raises(ProjectParseError) as execinfo:
        Project(dir_ex90_error_no_project)
    assert "路径下未找到 pyproject.toml" in str(execinfo.value)


def test_project_error_invalid_toml(
    dir_ex92_error_invalid_toml: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """测试TOML解析失败."""
    Project(dir_ex92_error_invalid_toml)
    assert "TOML解析错误" in caplog.text


def test_project_error_unkown_toml_error(
    dir_ex93_error_unkown_toml_encoding: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """测试TOML解析失败, 其他类型."""
    Project(dir_ex93_error_unkown_toml_encoding)
    assert "未知错误" in caplog.text


def test_project_error_invalid_source_ast(
    dir_ex94_error_invalid_source_ast: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """测试源文件AST解析错误."""
    Project(dir_ex94_error_invalid_source_ast)
    assert "源文件解析语法错误" in caplog.text


def test_project_error_invalid_project_config(
    dir_ex95_error_invalid_project_cfg: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """测试 pyproject.toml 解析依赖失败."""
    Project(dir_ex95_error_invalid_project_cfg)
    assert "配置项无效" in caplog.text


def test_project_error_invalid_pep621(
    dir_ex96_error_invalid_pep621: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """测试 pyproject.toml 解析依赖 pep621 失败."""
    Project(dir_ex96_error_invalid_pep621)
    assert "未设置项目参数[name]" in caplog.text
    assert "未设置项目参数[requires-python]" in caplog.text
    assert "依赖项格式错误" in caplog.text


def test_project_error_invalid_poetry_cfg(
    dir_ex98_error_invalid_poetry_cfg: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """测试 pyproject.toml 解析可选依赖失败."""
    Project(dir_ex98_error_invalid_poetry_cfg)
    assert "未设置项目参数[name]" in caplog.text
    assert "未指定python版本" in caplog.text
