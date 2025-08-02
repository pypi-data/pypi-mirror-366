from pathlib import Path

import pytest


@pytest.fixture
def dir_ex00_simple(dir_examples: Path) -> Path:
    return dir_examples / "ex00_simple"


@pytest.fixture
def dir_ex01_helloworld(dir_examples: Path) -> Path:
    return dir_examples / "ex01_helloworld"


@pytest.fixture
def dir_ex03_tkinter(dir_examples: Path) -> Path:
    return dir_examples / "ex03_tkinter"


@pytest.fixture
def dir_ex04_pyside2(dir_examples: Path) -> Path:
    return dir_examples / "ex04_pyside2"


@pytest.fixture
def dir_ex06_from_source(dir_examples: Path) -> Path:
    return dir_examples / "ex06_from_source"


@pytest.fixture
def dir_ex31_bottle(dir_examples: Path) -> Path:
    return dir_examples / "ex31_bottle"
