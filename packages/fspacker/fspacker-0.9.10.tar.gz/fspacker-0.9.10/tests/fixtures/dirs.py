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
def dir_ex09_poetry_py310(dir_examples: Path) -> Path:
    return dir_examples / "ex09_poetry_py310"


@pytest.fixture
def dir_ex31_bottle(dir_examples: Path) -> Path:
    return dir_examples / "ex31_bottle"


@pytest.fixture
def dir_ex90_error_no_project(dir_examples: Path) -> Path:
    return dir_examples / "ex90_error_no_project"


@pytest.fixture
def dir_ex91_error_no_source(dir_examples: Path) -> Path:
    return dir_examples / "ex91_error_no_source"


@pytest.fixture
def dir_ex92_error_invalid_toml(dir_examples: Path) -> Path:
    return dir_examples / "ex92_error_invalid_toml"


@pytest.fixture
def dir_ex93_error_unkown_toml_encoding(dir_examples: Path) -> Path:
    return dir_examples / "ex93_error_unkown_toml_encoding"


@pytest.fixture
def dir_ex94_error_invalid_source_ast(dir_examples: Path) -> Path:
    return dir_examples / "ex94_error_invalid_source_ast"


@pytest.fixture
def dir_ex95_error_invalid_project_cfg(dir_examples: Path) -> Path:
    return dir_examples / "ex95_error_invalid_project_cfg"


@pytest.fixture
def dir_ex96_error_invalid_pep621(dir_examples: Path) -> Path:
    return dir_examples / "ex96_error_invalid_pep621"


@pytest.fixture
def dir_ex98_error_invalid_poetry_cfg(dir_examples: Path) -> Path:
    return dir_examples / "ex98_error_invalid_poetry_cfg"
