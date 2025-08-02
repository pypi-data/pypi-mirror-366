from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

import pytest
from packaging.requirements import Requirement

from fspacker.utils.package import download_to_libs_dir
from fspacker.utils.package import extract_package_version
from fspacker.utils.package import get_cached_package
from fspacker.utils.package import is_version_satisfied
from fspacker.utils.package import unpack_wheel


@dataclass
class _Dirs:
    """模拟目录配置."""

    libs: Path


@pytest.fixture
def mock_cache_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """创建模拟的缓存目录.

    Returns:
        Path: 模拟的缓存目录
    """
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    class MockSettings:
        """模拟配置."""

        def __init__(self, libs_dir: Path) -> None:
            self.dirs = _Dirs(libs_dir)

    monkeypatch.setattr(
        "fspacker.utils.package.get_settings",
        lambda: MockSettings(cache_dir),
    )
    return cache_dir


@pytest.fixture
def mock_wheel_file(tmp_path: Path) -> Path:
    """创建模拟的wheel文件.

    Args:
        tmp_path: 临时目录路径

    Returns:
        Path: 模拟的wheel文件路径
    """
    wheel_file = tmp_path / "test_package-1.0.0-py3-none-any.whl"
    with ZipFile(wheel_file, "w") as zf:
        # 添加一些测试文件
        zf.writestr("test_package/__init__.py", "")
        zf.writestr("test_package/module.py", "print('Hello')")
        zf.writestr("test_package/data/data.txt", "some data")
        zf.writestr("test_package-1.0.0.dist-info/METADATA", "Metadata")
        zf.writestr("test_package-1.0.0.dist-info/RECORD", "Record")
    return wheel_file


class TestUnpackWheel:
    """测试解压wheel文件."""

    def test_basic_unpack(
        self,
        mock_wheel_file: Path,
        tmp_path: Path,
    ) -> None:
        """测试基本解压功能."""
        dest_dir = tmp_path / "output"
        unpack_wheel(mock_wheel_file, dest_dir)

        # 验证文件是否解压
        assert (dest_dir / "test_package/__init__.py").exists()
        assert (dest_dir / "test_package/module.py").exists()
        assert (dest_dir / "test_package/data/data.txt").exists()
        # dist-info 默认被排除
        assert not (dest_dir / "test_package-1.0.0.dist-info").exists()

    def test_unpack_with_excludes(
        self,
        mock_wheel_file: Path,
        tmp_path: Path,
    ) -> None:
        """测试使用excludes参数排除文件."""
        dest_dir = tmp_path / "output"
        excludes = {"test_package/data/*"}
        unpack_wheel(mock_wheel_file, dest_dir, excludes=excludes)

        # 验证文件是否解压
        assert (dest_dir / "test_package/__init__.py").exists()
        assert (dest_dir / "test_package/module.py").exists()
        # data目录被排除
        assert not (dest_dir / "test_package/data/data.txt").exists()
        # dist-info 默认被排除
        assert not (dest_dir / "test_package-1.0.0.dist-info").exists()

    def test_unpack_with_patterns(
        self,
        mock_wheel_file: Path,
        tmp_path: Path,
    ) -> None:
        """测试使用patterns参数只解压特定文件."""
        dest_dir = tmp_path / "output"
        patterns = {"test_package/*.py"}
        unpack_wheel(mock_wheel_file, dest_dir, patterns=patterns)

        # 只有.py文件被解压
        assert (dest_dir / "test_package/__init__.py").exists()
        assert (dest_dir / "test_package/module.py").exists()
        # 其他文件不被解压
        assert not (dest_dir / "test_package/data/data.txt").exists()
        assert not (dest_dir / "test_package-1.0.0.dist-info").exists()

    def test_unpack_with_excludes_and_patterns(
        self,
        mock_wheel_file: Path,
        tmp_path: Path,
    ) -> None:
        """测试组合使用excludes和patterns."""
        dest_dir = tmp_path / "output"
        excludes = {"test_package/module.py"}
        patterns = {"test_package/*.py"}
        unpack_wheel(
            mock_wheel_file,
            dest_dir,
            excludes=excludes,
            patterns=patterns,
        )

        # module.py被排除
        assert (dest_dir / "test_package/__init__.py").exists()
        assert not (dest_dir / "test_package/module.py").exists()
        # 其他文件不被解压
        assert not (dest_dir / "test_package/data/data.txt").exists()
        assert not (dest_dir / "test_package-1.0.0.dist-info").exists()

    def test_empty_wheel(
        self,
        tmp_path: Path,
    ) -> None:
        """测试空wheel文件."""
        empty_wheel = tmp_path / "empty-1.0.0-py3-none-any.whl"
        with ZipFile(empty_wheel, "w"):
            pass  # 创建空zip文件

        dest_dir = tmp_path / "output"
        unpack_wheel(empty_wheel, dest_dir)

        # 确保没有文件被解压
        assert not any(dest_dir.iterdir())


class TestDownloadToLibsDir:
    """测试下载到缓存."""

    @pytest.fixture
    def mock_settings(
        self,
        mock_cache_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """模拟配置."""
        pip_url = "https://pypi.tuna.tsinghua.edu.cn/simple"

        @dataclass
        class MockUrls:
            fastest_pip_url: str = pip_url

        class MockSettings:
            def __init__(self, libs_dir: Path) -> None:
                self.dirs = _Dirs(libs_dir)
                self.urls = MockUrls()
                self.python_exe = "python"

        monkeypatch.setattr(
            "fspacker.utils.package.get_settings",
            lambda: MockSettings(mock_cache_dir),
        )

    def test_download_success(
        self,
        mock_settings: None,  # noqa: ARG002
        mock_cache_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """测试成功下载包."""

        # 模拟subprocess.call成功
        def mock_call(cmd: str, *, shell: bool) -> int:  # noqa: ARG001
            # 创建一个模拟的下载文件
            package_path = (
                mock_cache_dir / "numpy-1.19.2-cp39-cp39-win_amd64.whl"
            )
            package_path.touch()
            return 0

        monkeypatch.setattr(subprocess, "call", mock_call)

        req = Requirement("numpy>=1.19.0")
        result = download_to_libs_dir(req)

        assert result is not None
        assert result.name == "numpy-1.19.2-cp39-cp39-win_amd64.whl"
        assert result.parent == mock_cache_dir

    def test_download_failure(
        self,
        mock_settings: None,  # noqa: ARG002
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """测试下载失败."""

        # 模拟subprocess.call失败
        def mock_call(cmd: str, *, shell: bool) -> int:  # noqa: ARG001
            return 1

        monkeypatch.setattr(subprocess, "call", mock_call)

        req = Requirement("nonexistent-package>=1.0.0")
        result = download_to_libs_dir(req)

        assert result == Path()

    def test_download_existing_package(
        self,
        mock_settings: None,  # noqa: ARG002
        mock_cache_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """测试下载已存在的包."""
        # 预先创建一个满足版本要求的包文件
        package_name = "numpy-1.19.2-cp39-cp39-win_amd64.whl"
        package_path = mock_cache_dir / package_name
        package_path.touch()

        def mock_call(cmd: str, *, shell: bool) -> int:  # noqa: ARG001
            return 0

        # 模拟subprocess.cal, 确保不会实际执行pip下载
        monkeypatch.setattr(subprocess, "call", mock_call)

        req = Requirement("numpy>=1.19.0")
        result = download_to_libs_dir(req)

        assert result is not None
        assert result.name == package_name
        assert result.parent == mock_cache_dir


class TestExtractPackageVersion:
    """测试从文件名提取版本号."""

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("numpy-1.19.2-cp39-cp39-win_amd64.whl", "1.19.2"),
            ("pandas-1.3.0-cp39-cp39-win_amd64.whl", "1.3.0"),
            ("requests-2.25.1-py2.py3-none-any.whl", "2.25.1"),
            ("scipy-1.7.0-cp39-cp39-win_amd64.whl", "1.7.0"),
        ],
    )
    def test_extract_package_version(
        self,
        filename: str,
        expected: str,
    ) -> None:
        """测试从文件名提取版本号."""
        version = extract_package_version(filename)
        assert version == expected

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("invalid-package-name.whl", "0.0.0"),
            ("package-without-version.whl", "0.0.0"),
            ("package-1.0-invalid.format", "1.0"),
        ],
    )
    def test_extract_package_version_invalid(
        self,
        filename: str,
        expected: str,
    ) -> None:
        """测试从无效文件名提取版本号."""
        version = extract_package_version(filename)
        assert version == expected


class TestGetCachedPackage:
    """测试从缓存获取包."""

    def test_get_cached_package_not_found(self) -> None:
        """测试获取不存在的缓存包."""
        req = Requirement("nonexistent-package>=1.0.0")
        result = get_cached_package(req)
        assert result is None

    def test_get_cached_package_found(self, mock_cache_dir: Path) -> None:
        """测试获取存在的缓存包."""
        # 创建模拟的包文件
        package_name = "numpy-1.19.2-cp39-cp39-win_amd64.whl"
        package_path = mock_cache_dir / package_name
        package_path.touch()

        req = Requirement("numpy>=1.19.0")
        result = get_cached_package(req)
        assert result is not None
        assert result.name == package_name

    def test_get_cached_package_version_mismatch(
        self,
        mock_cache_dir: Path,
    ) -> None:
        """测试获取版本不匹配的缓存包."""
        # 创建模拟的包文件
        package_name = "numpy-1.19.2-cp39-cp39-win_amd64.whl"
        package_path = mock_cache_dir / package_name
        package_path.touch()

        req = Requirement("numpy>=2.0.0")
        result = get_cached_package(req)
        assert result is None

    def test_get_cached_package_multiple_versions(
        self,
        mock_cache_dir: Path,
    ) -> None:
        """测试存在多个版本时返回按文件名排序的第一个匹配版本."""
        # 创建多个版本的包文件
        packages = [
            "numpy-1.19.2-cp39-cp39-win_amd64.whl",
            "numpy-1.20.0-cp39-cp39-win_amd64.whl",
            "numpy-1.21.0-cp39-cp39-win_amd64.whl",
        ]
        for package in packages:
            (mock_cache_dir / package).touch()

        req = Requirement("numpy>=1.19.0")
        result = get_cached_package(req)
        assert result is not None
        # 根据实际行为, 函数返回按文件名排序的第一个匹配版本
        assert result.name == "numpy-1.19.2-cp39-cp39-win_amd64.whl"


class TestIsVersionSatisfied:
    """测试版本满足条件判断."""

    @pytest.mark.parametrize(
        ("filename", "requirement", "expected"),
        [
            (
                "numpy-1.19.2-cp39-cp39-win_amd64.whl",
                "numpy>=1.19.0",
                True,
            ),
            (
                "numpy-1.19.2-cp39-cp39-win_amd64.whl",
                "numpy==1.19.2",
                True,
            ),
            (
                "numpy-1.19.2-cp39-cp39-win_amd64.whl",
                "numpy>2.0.0",
                False,
            ),
            (
                "pandas-1.3.0-cp39-cp39-win_amd64.whl",
                "pandas>=1.0.0,<2.0.0",
                True,
            ),
            (
                "pandas-1.3.0-cp39-cp39-win_amd64.whl",
                "pandas<1.0.0",
                False,
            ),
        ],
    )
    def test_version_satisfaction(
        self,
        filename: str,
        requirement: str,
        *,
        expected: bool,
    ) -> None:
        """测试版本满足条件判断."""
        req = Requirement(requirement)
        result = is_version_satisfied(Path(filename), req)
        assert result == expected
