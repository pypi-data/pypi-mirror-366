from fspacker.simplifiers import get_simplify_options
from fspacker.simplifiers import SimplifierOption


def test_get_simplify_options_existing() -> None:
    """测试获取已存在的库的精简配置."""
    option = get_simplify_options("pyside2")
    assert isinstance(option, SimplifierOption)
    assert option.patterns is not None
    assert "PySide2/__init__.py" in option.patterns


def test_get_simplify_options_nonexistent() -> None:
    """测试获取不存在的库的精简配置."""
    option = get_simplify_options("nonexistent_lib")
    assert option is None


def test_simplifier_option_dataclass() -> None:
    """测试 SimplifierOption 是否为 dataclass."""
    option = SimplifierOption(patterns={"a"}, excludes={"b"})
    assert option.patterns == {"a"}
    assert option.excludes == {"b"}
