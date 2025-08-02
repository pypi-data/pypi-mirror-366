from __future__ import annotations

import pytest

from fspacker.exceptions import ProjectPackError
from fspacker.utils.requirement import RequirementParser


class TestRequirementParser:
    """测试需求字符串解析器."""

    @pytest.mark.parametrize(
        ("source", "dest"),
        [
            (
                "numpy ~= 1.19 ; python_version>'3.6'",
                "numpy~=1.19",
            ),  # 处理环境标记前的空格
            ("shiboken2 (==5.15.2.1)", "shiboken2==5.15.2.1"),  # 括号包裹版本
            ("package@1.0 # 注释", "package==1.0"),  # 替换@符号并移除注释
            ("pandas >=1.1, <2.0", "pandas>=1.1,<2.0"),  # 标准化运算符空格
            ("scipy ; extra == 'analysis'", "scipy"),  # 移除分号后的环境标记
        ],
    )
    def test_normalization_cases(self, source: str, dest: str) -> None:
        """测试需求字符串规范化."""
        result = RequirementParser.normalize(source)
        assert result == dest

    @pytest.mark.parametrize(
        ("source", "parsed"),
        [
            (
                "requests==2.25.1; sys_platform=='linux'",
                {
                    "name": "requests",
                    "specifier": "==2.25.1",
                    "marker": "sys_platform=='linux'",
                },
            ),
            ("django~=3.2.0", {"name": "django", "specifier": "~=3.2.0"}),
        ],
    )
    def test_parse_valid_requirements(
        self,
        source: str,
        parsed: dict[str, str],
    ) -> None:
        """测试解析有效需求字符串."""
        req = RequirementParser.parse(source)
        assert req
        assert req.name == parsed.get("name")
        assert req.specifier == parsed.get("specifier")

    @pytest.mark.parametrize(
        "req",
        [
            "invalid/package==1.0",  # 非法包名
            "missing_version@",  # 不完整版本
            "==1.0",  # 缺少包名
            "package>=1.0<2.0",  # 缺少逗号分隔符
        ],
    )
    def test_invalid_requirements(self, req: str) -> None:
        """测试非法字符串异常捕获."""
        with pytest.raises(ProjectPackError) as _:
            RequirementParser.parse(req)
