from __future__ import annotations

import fnmatch
import logging
import pathlib
import re
import subprocess
import zipfile
from pathlib import Path
from urllib.parse import urlparse

from packaging import requirements

from fspacker.settings import get_settings
from fspacker.simplifiers import get_simplify_options
from fspacker.trackers import perf_tracker

logger = logging.getLogger(__name__)


def is_version_satisfied(
    cached_file: Path,
    req: requirements.Requirement,
) -> bool:
    """检查缓存文件版本是否满足需求.

    Args:
        cached_file: 缓存文件.
        req: 依赖.

    Returns:
        bool: 是否满足版本约束.
    """
    if not req.specifier:
        return True  # 无版本约束

    version = extract_package_version(cached_file.name)
    return version in req.specifier


def get_cached_package(
    req: requirements.Requirement,
) -> Path | None:
    """获取满足版本约束的缓存文件.

    Args:
        req: 依赖.

    Returns:
        pathlib.Path: 满足版本约束的缓存文件, 无则返回None.
    """

    def to_case_insensitive(pattern: str) -> str:
        # 将每个字母替换为大小写组合
        return "".join(
            f"[{c.lower()}{c.upper()}]" if c.isalpha() else c for c in pattern
        )

    package_name = req.name.lower().replace("-", "_")  # 包名大小写不敏感
    pattern = (
        f"{package_name}-*" if not req.specifier else f"{package_name}-[0-9]*"
    )

    # 查找所有匹配的缓存文件, 使用sorted确保文件名顺序一致
    # 以避免因大小写不同导致的匹配问题
    cached_files = sorted(
        get_settings().dirs.libs.glob(
            to_case_insensitive(pattern),
        ),
        key=lambda x: str(x).lower(),
    )

    for cached_file in cached_files:
        if cached_file.suffix in {
            ".whl",
            ".gz",
            ".zip",
        } and is_version_satisfied(cached_file, req):
            return cached_file
    return None


def download_to_libs_dir(req: requirements.Requirement) -> Path:
    """下载满足版本的包到缓存.

    Args:
        req: 依赖.

    Returns:
        Path: 下载的文件.
    """
    pip_url = get_settings().urls.fastest_pip_url
    net_loc = urlparse(pip_url).netloc
    libs_dir = get_settings().dirs.libs
    libs_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        get_settings().python_exe,
        "-m",
        "pip",
        "download",
        "--no-deps",
        "--dest",
        str(libs_dir),
        str(req),  # 使用解析后的Requirement对象保持原始约束
        "--trusted-host",
        net_loc,
        "-i",
        pip_url,
        "--no-deps",
    ]

    subprocess.call(cmd, shell=False)
    lib_filepath = get_cached_package(req) or pathlib.Path()
    logger.info(f"下载后库文件: [[green bold]{lib_filepath.name}[/]]")
    return lib_filepath


@perf_tracker
def unpack_wheel(
    wheel_file: Path,
    dest_dir: Path,
    excludes: set[str] | None = None,
    patterns: set[str] | None = None,
) -> None:
    if not dest_dir.exists():
        logger.info(f"创建目标目录: [[green bold]{dest_dir}[/]]")
        dest_dir.mkdir(parents=True)

    excludes = set() if excludes is None else excludes
    patterns = set() if patterns is None else patterns

    excludes = set(excludes) | {"*dist-info/*"}
    with zipfile.ZipFile(wheel_file, "r") as zf:
        for file in zf.namelist():
            if any(fnmatch.fnmatch(file, exclude) for exclude in excludes):
                continue

            if len(patterns):
                if any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                    zf.extract(file, dest_dir)
                    continue
                continue

            zf.extract(file, dest_dir)


@perf_tracker
def install_package(
    req: requirements.Requirement,
    lib_file: Path,
    dest_dir: Path,
    *,
    simplify: bool = False,
) -> None:
    """从缓存安装到site-packages."""
    options = get_simplify_options(req.name)

    if simplify and options:
        excludes, patterns = options.excludes, options.patterns
        logger.info(
            f"找到简化目标库: {req.name}, {options.excludes=}, "
            f"{options.patterns=}",
        )
    else:
        excludes, patterns = None, None
        logger.error(f"未找到简化目标库: {req.name}")

    if lib_file.suffix == ".whl":
        unpack_wheel(lib_file, dest_dir, excludes, patterns)
    else:
        cmds = [
            get_settings().python_exe,
            "-m",
            "pip",
            "install",
            str(lib_file.absolute()),
            "-t",
            str(dest_dir),
        ]
        logger.info(f"调用命令: [green bold]{cmds}")
        subprocess.call(cmds, shell=False)


def extract_package_version(filename: str) -> str:
    """从文件名提取版本号, 支持任意长度版本号如 20.0 或 1.20.3.4.

    适配格式:
       package-1.2.3.tar.gz
       package-20.0-py3-none-any.whl
       Package_Name-1.20.3.4.whl

    Args:
        filename: 文件名.

    Returns:
        str: 版本号.
    """
    version_pattern = r"""
        (?:^|-)                   # 开头或连接符
        (\d+\.\d+(?:\.\d+)*)      # 版本号核心(至少两段数字)
        (?=-|\.|_|$)              # 后接分隔符或结束
    """
    match = re.search(version_pattern, filename, re.VERBOSE)
    return match.group(1) if match else "0.0.0"  # 默认返回最低版本
