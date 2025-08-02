from __future__ import annotations

from pathlib import Path

import pytest

from fspacker.exceptions import ProjectParseError
from fspacker.parsers.project import Project


class TestPoetryProject:
    """Test poetry project."""

    def test_helloworld(
        self,
        mock_console_helloworld: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test hello world project."""
        info = Project(mock_console_helloworld)

        assert info.name == "test-console-helloworld"
        assert not info.is_gui
        assert info.license_file
        assert info.source_file
        assert info.source_file.name == "main.py"

        # set gui mode
        monkeypatch.setattr("fspacker.settings._settings.mode.gui", True)
        assert info.is_gui

    def test_nomain(self, mock_console_nomain: Path) -> None:
        """Test no main project."""
        info = Project(mock_console_nomain)

        assert info.name == "test-console-nomain"
        assert not info.is_gui
        assert not info.license_file
        assert not info.source_file

    def test_multi_py310(self, mock_multi_py310: Path) -> None:
        """Test python 3.10 project."""
        info = Project(mock_multi_py310)

        assert info.name == "test-multi-py310"
        assert info.authors == ["Your Name <you@example.com>"]
        assert info.dependencies == [
            "pygame<2.7.0,>=2.6.1",
            "tomli<3.0.0,>=2.2.1",
            "typer>=0.15.2",
        ]
        assert info.python_specifiers == ">=3.10,<4.0"
        assert info.is_gui

    def test_pygame(self, mock_pygame: Path) -> None:
        """Test pygame project."""
        info = Project(mock_pygame)

        assert info.name == "test-pygame"
        assert info.dependencies == ["pygame>=2.6.1"]
        assert info.python_specifiers == ">=3.6"
        assert info.is_gui
        assert info.is_normal_project

        assert info.dest_src_dir == mock_pygame / "dist" / "src" / "test_pygame"
        assert info.source_file
        assert info.source_file.name == "main.py"

    def test_pyside2(self, mock_pyside2: Path) -> None:
        """Test pyside2 project."""
        info = Project(mock_pyside2)

        assert info.name == "test-pyside2"
        assert info.dependencies == ["pyside2>=5.15.2.1"]
        assert info.python_specifiers == ">=3.8"
        assert info.is_gui
        assert not info.is_normal_project


class TestProjectParseTomlError:
    """Test project parse toml error."""

    def test_invalid_project_path(self) -> None:
        """Test invalid project path."""
        # Test project path is None.
        with pytest.raises(ProjectParseError) as execinfo:
            Project(None)
        assert "Invalid project directory: None" in str(execinfo.value)

        # Test project path is not exists.
        with pytest.raises(ProjectParseError) as execinfo:
            Project(Path("nonexistent_dir"))
        assert "Invalid project directory: nonexistent_dir" in str(
            execinfo.value,
        )

    def test_no_toml_file(self, tmp_path: Path) -> None:
        """测试没有项目文件."""
        with pytest.raises(ProjectParseError) as execinfo:
            Project(tmp_path)

        assert "路径下未找到 pyproject.toml" in str(execinfo.value)

    def test_unkown_toml_error(
        self,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试TOML解析失败, 其他类型."""
        project_dir = tmp_path / "project_unkown_toml"
        project_dir.mkdir()

        pyproject_toml = project_dir / "pyproject.toml"
        pyproject_toml.write_text(
            """
            hello, world!
            """,
            encoding="utf-16",
        )

        Project(project_dir)

        assert "未知错误" in caplog.text

        pyproject_toml.write_text("不正确的Toml文件", encoding="utf-8")
        Project(project_dir)
        assert "TOML解析错误" in caplog.text

    def test_invalid_source_ast(
        self,
        mock_console_invalid_ast: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试源文件AST解析错误."""
        Project(mock_console_invalid_ast)

        assert "源文件解析语法错误" in caplog.text

    def test_invalid_project_config(
        self,
        mock_console_helloworld: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试 pyproject.toml 解析依赖失败."""
        project_dir = mock_console_helloworld
        assert project_dir.exists()

        pyproject_toml = project_dir / "pyproject.toml"
        pyproject_toml.write_text(
            """
    [invalidprojectconfig]
    name = "ex95-error-invalid-project-cfg"
    version = "0.1.0"
    description = "Add your description here"
    readme = "README.md"
    requires-python = ">=3.8"
    dependencies = []""",
            encoding="utf-8",
        )

        Project(project_dir)

        assert "配置项无效" in caplog.text

    def test_invalid_pep621(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试 pyproject.toml 解析依赖 pep621 失败."""
        project_dir = tmp_path_factory.mktemp("test-invalid-pep621")
        pyproject_toml = project_dir / "pyproject.toml"
        pyproject_toml.write_text(
            """
    [project]
    version = "0.1.0"
    description = "Add your description here"
    readme = "README.md"
    dependencies = "error"
    optional-dependencies = "error"
    """,
            encoding="utf-8",
        )
        main_file = project_dir / "main.py"
        main_file.write_text(
            """
def main():
    print("Test for poetry project!")

main()
    """,
            encoding="utf-8",
        )

        Project(project_dir)

        assert "未设置项目参数[name]" in caplog.text
        assert "未设置项目参数[requires-python]" in caplog.text
        assert "依赖项格式错误" in caplog.text

    def test_invalid_poetry_cfg(
        self,
        mock_console_helloworld: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试 pyproject.toml 解析可选依赖失败."""
        project_dir = mock_console_helloworld
        assert project_dir.exists()

        # 创建一个无效的poetry配置文件
        pyproject_toml = project_dir / "pyproject.toml"
        pyproject_toml.write_text(
            """
    [tool.poetry]
    version = "0.1.0"
    description = ""
    authors = ["test <test@example.com>"]
    readme = "README.md"

    [tool.poetry.dependencies]

    [build-system]
    requires = ["poetry-core"]
    build-backend = "poetry.core.masonry.api"
    """,
            encoding="utf-8",
        )

        Project(project_dir)

        assert "未设置项目参数[name]" in caplog.text
        assert "未指定python版本" in caplog.text
