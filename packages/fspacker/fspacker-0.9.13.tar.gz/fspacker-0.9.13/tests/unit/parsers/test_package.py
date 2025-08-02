from __future__ import annotations

import platform
import zipfile
from pathlib import Path

from fspacker.parsers.package import PackageFileDependencyAnalyzer


class TestPackageFileDependencyAnalyzer:
    """测试包文件依赖项分析器."""

    def test_analyze_dependencies_filter_extras(self, tmp_path: Path) -> None:
        """测试分析依赖项时过滤extras依赖."""
        # 创建一个模拟的METADATA文件内容
        metadata_content = """Metadata-Version: 2.1
Name: test-package
Version: 1.0.0
Requires-Dist: requests
Requires-Dist: numpy; extra == 'scientific'
Requires-Dist: pandas; extra == 'data'
Requires-Dist: flask; extra == 'web'
Requires-Dist: django (>=3.0); extra == 'web' and python_version >= "3.6"
"""

        # 创建模拟的wheel文件
        dist_info_path = tmp_path / "test_package-1.0.0.dist-info"
        dist_info_path.mkdir()

        metadata_file = dist_info_path / "METADATA"
        metadata_file.write_text(metadata_content)

        # 创建wheel文件
        wheel_file = tmp_path / "test_package-1.0.0-py3-none-any.whl"

        with zipfile.ZipFile(wheel_file, "w") as zf:
            zf.write(metadata_file, "test_package-1.0.0.dist-info/METADATA")

        # 分析依赖项
        requirements = PackageFileDependencyAnalyzer.analyze_dependencies(
            wheel_file,
        )

        # 验证结果 - 只应该包含不带extra的依赖项
        assert len(requirements) == 1
        assert requirements[0].name == "requests"

    def test_analyze_dependencies_filter_by_environment(
        self,
        tmp_path: Path,
    ) -> None:
        """测试分析依赖项时根据环境过滤."""
        # 创建一个模拟的METADATA文件内容
        current_system = platform.system().lower()
        other_system = "windows" if current_system != "windows" else "linux"

        metadata_content = f"""Metadata-Version: 2.1
Name: test-package
Version: 1.0.0
Requires-Dist: requests
Requires-Dist: numpy; sys_platform == '{other_system}'
Requires-Dist: pandas; python_version < '3.0'
Requires-Dist: flask; python_version >= '3.8'
"""

        # 创建模拟的wheel文件
        dist_info_path = tmp_path / "test_package-1.0.0.dist-info"
        dist_info_path.mkdir()

        metadata_file = dist_info_path / "METADATA"
        metadata_file.write_text(metadata_content)

        # 创建wheel文件
        wheel_file = tmp_path / "test_package-1.0.0-py3-none-any.whl"

        with zipfile.ZipFile(wheel_file, "w") as zf:
            zf.write(metadata_file, "test_package-1.0.0.dist-info/METADATA")

        # 分析依赖项
        requirements = PackageFileDependencyAnalyzer.analyze_dependencies(
            wheel_file,
        )

        # 应该包含requests和满足条件的flask, 但不包含不满足环境条件的依赖
        assert len(requirements) == 2  # noqa: PLR2004
        names = [req.name for req in requirements]
        assert "requests" in names
        assert "flask" in names
        assert "numpy" not in names  # 不应该包含不匹配当前系统的依赖
        assert "pandas" not in names  # 不应该包含不匹配Python版本的依赖

    def test_analyze_dependencies_combined_filters(
        self,
        tmp_path: Path,
    ) -> None:
        """测试分析依赖项时同时应用多种过滤."""
        # 创建一个模拟的METADATA文件内容
        current_system = platform.system().lower()
        other_system = "windows" if current_system != "windows" else "linux"

        metadata_content = f"""Metadata-Version: 2.1
Name: test-package
Version: 1.0.0
Requires-Dist: requests
Requires-Dist: numpy; sys_platform == '{other_system}'
Requires-Dist: pandas; python_version < '3.0'
Requires-Dist: flask; python_version >= '3.8'
Requires-Dist: django (>=3.0); extra == 'web' and python_version >= "3.6"
Requires-Dist: pytz; sys_platform == '{current_system}' and extra == 'time'
"""

        # 创建模拟的wheel文件
        dist_info_path = tmp_path / "test_package-1.0.0.dist-info"
        dist_info_path.mkdir()

        metadata_file = dist_info_path / "METADATA"
        metadata_file.write_text(metadata_content)

        # 创建wheel文件
        wheel_file = tmp_path / "test_package-1.0.0-py3-none-any.whl"

        with zipfile.ZipFile(wheel_file, "w") as zf:
            zf.write(metadata_file, "test_package-1.0.0.dist-info/METADATA")

        # 分析依赖项
        requirements = PackageFileDependencyAnalyzer.analyze_dependencies(
            wheel_file,
        )

        # 验证结果 - 应该只包含requests和满足条件的flask
        assert len(requirements) == 2  # noqa: PLR2004
        names = [req.name for req in requirements]
        assert "requests" in names
        assert "flask" in names
        # 不应该包含带extra的依赖或者不匹配环境的依赖
        assert "numpy" not in names
        assert "pandas" not in names
        assert "django" not in names
        assert "pytz" not in names
