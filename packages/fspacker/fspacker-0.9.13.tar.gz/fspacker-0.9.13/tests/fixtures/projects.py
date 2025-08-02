from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest


@pytest.fixture(scope="session")
def mock_create_project_file(
    tmp_path_factory: pytest.TempPathFactory,
) -> Callable[[str], Path]:
    """Mock project file.

    Returns:
        Function that creates a mock project file.
    """

    def create_project_file(
        name: str,
        requires_python: str = ">=3.8",
        dependencies: list[str] | None = None,
    ) -> Path:
        if dependencies is None:
            dependencies = []

        project_dir = tmp_path_factory.mktemp(name)
        project_file = project_dir / "pyproject.toml"
        project_file.write_text(
            f"""
    [project]
    name = "{name}"
    version = "0.1.0"
    description = "A simple project."
    authors = []
    requires-python = "{requires_python}"
    dependencies = {dependencies}
    """,
            encoding="utf-8",
        )
        return project_dir

    return create_project_file


@pytest.fixture(scope="session")
def mock_console_helloworld(
    mock_create_project_file: Callable[[str], Path],
) -> Path:
    """Console helloworld project.

    Returns:
        Path: Path to the project directory.
    """
    project_dir = mock_create_project_file("test-console-helloworld")
    main_file = project_dir / "main.py"
    main_file.write_text(
        """
def main() -> None:
    print("hello world!")

if __name__ == "__main__":
    main()
""",
        encoding="utf-8",
    )

    license_file = project_dir / "LICENSE.txt"
    license_file.write_text(
        """
MIT License

Copyright (c) 2023 FS-Packager

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

""",
        encoding="utf-8",
    )

    return project_dir


@pytest.fixture(scope="session")
def mock_console_nomain(
    mock_create_project_file: Callable[[str], Path],
) -> Path:
    """Console project with no main source.

    Returns:
        Path: Path to the project directory.
    """
    project_dir = mock_create_project_file("test-console-nomain")
    main_file = project_dir / "main.py"
    main_file.write_text(
        """
def hello() -> None:
    print("hello world!")

hello()
""",
        encoding="utf-8",
    )
    return project_dir


@pytest.fixture(scope="session")
def mock_console_with_venv(
    mock_pygame: Path,
) -> Path:
    venv_dir = mock_pygame / ".venv"
    venv_dir.mkdir()

    invalid_main_file = venv_dir / "invalid_main.py"
    invalid_main_file.write_text(
        """
def main():
    print("hello world!")

main()
""",
        encoding="utf-8",
    )

    return mock_pygame


@pytest.fixture(scope="session")
def mock_console_invalid_ast(
    mock_create_project_file: Callable[[str], Path],
) -> Path:
    """Console project with invalid ast.

    Returns:
        Path: Path to the project directory.
    """
    project_dir = mock_create_project_file("test-console-invalid-ast")
    main_file = project_dir / "main.py"
    main_file.write_text(
        """
import

def main() -> None:
    print("hello world!")

if __name__ == "__main__":
    main()
""",
        encoding="utf-8",
    )

    return project_dir


@pytest.fixture(scope="session")
def mock_multi_py310(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Virtual project directory for poetry project.

    Returns:
        Path: Path to the virtual project directory.
    """
    project_dir = tmp_path_factory.mktemp("test-multi-py310")
    project_file = project_dir / "pyproject.toml"
    project_file.write_text(
        """
[tool.poetry]
name = "test-multi-py310"
version = "0.1.0"
description = ""
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.10"
pygame = "~2.6.1"
tomli = "^2.2.1"
typer = ">=0.15.2"

[tool.poetry.group.dev.dependencies]
tomli = "^2.2.1"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[[tool.poetry.source]]
name = 'tuna'
url = 'https://pypi.tuna.tsinghua.edu.cn/simple/'
priority = "primary"

[[tool.poetry.source]]
name = 'aliyun'
url = 'https://mirrors.aliyun.com/pypi/'
priority = "supplemental"
""",
        encoding="utf-8",
    )

    main_file = project_dir / "main.py"
    main_file.write_text(
        """
import pygame
import tomli
import typer


def main():
    print("Test for poetry project!")
    print("Pygame version:", pygame.__version__)
    print("Tomli version:", tomli.__version__)
    print("Typer version:", typer.__version__)


if __name__ == "__main__":
    main()
""",
        encoding="utf-8",
    )

    return project_dir


@pytest.fixture(scope="session")
def mock_pygame(
    mock_create_project_file: Callable[[str, str, list[str]], Path],
) -> Path:
    project_dir = mock_create_project_file(
        "test-pygame",
        ">=3.6",
        ["pygame>=2.6.1"],
    )

    # Create source file under `src/test_pygame`
    source_dir = project_dir / "src" / "test_pygame"
    source_dir.mkdir(parents=True, exist_ok=True)

    main_file = source_dir / "main.py"
    main_file.write_text(
        """
from __future__ import annotations
import pygame

def main(args: list[str] = list("123")):
    print(f"Hello from test_pygame! {args}")

    pygame.init()

    screen = pygame.display.set_mode((640, 480))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

main()
""",
        encoding="utf-8",
    )
    return project_dir


@pytest.fixture(scope="session")
def mock_pyside2(
    mock_create_project_file: Callable[[str, str, list[str]], Path],
) -> Path:
    project_dir = mock_create_project_file(
        "test-pyside2",
        ">=3.8",
        ["PySide2>=5.15.2.1"],
    )

    # Create main.py under project directory
    main_file = project_dir / "main.py"
    main_file.write_text(
        """
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

def main() -> None:
    app = QApplication([])

    win = QWidget()
    win.setWindowTitle("pyside2 simple gui")

    layout = QVBoxLayout()
    label = QLabel("Hello, Pyside2!")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    btn = QPushButton(text="PUSH ME")
    layout.addWidget(btn)

    win.setLayout(layout)
    win.resize(400, 300)

    btn.clicked.connect(
        lambda: [
            print("exit"),
            win.close(),
        ],
    )

    win.show()
    app.exec_()


if __name__ == "__main__":
    main()
""",
        encoding="utf-8",
    )

    return project_dir
