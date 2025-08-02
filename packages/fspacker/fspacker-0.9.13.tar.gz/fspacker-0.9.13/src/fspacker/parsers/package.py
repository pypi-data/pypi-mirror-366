from __future__ import annotations

import email.message
import logging
import os
import pathlib
import platform
import sys
import tarfile
import zipfile
from pathlib import Path

from packaging.markers import Marker
from packaging.requirements import InvalidRequirement
from packaging.requirements import Requirement

from fspacker.exceptions import ProjectPackError
from fspacker.utils.requirement import RequirementParser

__all__ = ["analyze_package_deps"]

logger = logging.getLogger(__name__)


class PackageFileDependencyAnalyzer:
    @staticmethod
    def extract_metadata(
        package_path: Path,
    ) -> email.message.Message | None:
        """从包文件中提取元数据.

        Args:
            package_path (Path): 包文件路径.

        Returns:
            email.message.Message | None: 包文件元数据.
        """
        if package_path.suffix == ".whl":
            return PackageFileDependencyAnalyzer.parse_wheel_metadata(
                package_path,
            )

        if package_path.suffix in {".gz", ".zip"}:
            logger.info(f"找到压缩包库文件: {package_path}")
            return PackageFileDependencyAnalyzer.parse_gz_metadata(package_path)

        return None

    @staticmethod
    def parse_gz_metadata(
        package_path: Path,
    ) -> email.message.Message | None:
        """从 gz 包元数据中提取依赖项.

        Args:
            package_path (Path): 包文件路径.

        Returns:
            email.message.Message | None: 包文件元数据.
        """
        opener = (
            tarfile.open if package_path.suffix == ".gz" else zipfile.ZipFile
        )
        with opener(package_path) as archive:
            if isinstance(archive, tarfile.TarFile):
                for member in archive.getmembers():
                    if member.name.endswith(("PKG-INFO", "METADATA")):
                        fileobj = archive.extractfile(member)
                        if not fileobj:
                            logger.warning("无法提取文件: %s", member.name)
                            continue
                        metadata = fileobj.read().decode("utf-8")
                        return email.message_from_string(metadata)

        logger.warning("无法提取压缩包库文件: %s", package_path)
        return None

    @staticmethod
    def parse_wheel_metadata(
        package_path: Path,
    ) -> email.message.Message | None:
        """从 wheel 包元数据中提取依赖项.

        Args:
            package_path (Path): 包文件路径.

        Returns:
            email.message.Message | None: 包文件元数据.
        """
        with zipfile.ZipFile(package_path) as z:
            for name in z.namelist():
                if name.endswith(".dist-info/METADATA"):
                    metadata = z.read(name).decode("utf-8")
                    return email.message_from_string(metadata)
        return None

    @classmethod
    def analyze_dependencies(
        cls,
        package_path: Path,
    ) -> list[Requirement]:
        metadata = cls.extract_metadata(package_path)
        if not metadata:
            return []

        requirements = []
        for field in ["Requires-Dist", "Requires"]:
            for req_str in metadata.get_all(field, []):
                # 使用RequirementParser.parse来正确解析依赖项
                try:
                    req = RequirementParser.parse(req_str)
                    if req:
                        # 过滤掉包含extra的依赖项
                        if req.marker and "extra" in str(req.marker):
                            continue

                        # 过滤掉不适用于当前环境的依赖项
                        if req.marker and not cls._evaluate_marker(req.marker):
                            continue

                        requirements.append(req)
                except (InvalidRequirement, ProjectPackError):
                    # 忽略无法解析的依赖项
                    continue

        return requirements

    @classmethod
    def _evaluate_marker(cls, marker: Marker) -> bool:
        """评估marker是否适用于当前环境.

        Returns:
            bool: marker是否适用于当前环境.
        """
        # 构建当前环境信息字典
        environment = {
            "python_version": ".".join(platform.python_version_tuple()[:2]),
            "python_full_version": platform.python_version(),
            "os_name": os.name,
            "sys_platform": sys.platform,
            "platform_machine": platform.machine(),
            "platform_python_implementation": platform.python_implementation(),
            "platform_release": platform.release(),
            "platform_system": platform.system(),
            "platform_version": platform.version(),
        }

        return marker.evaluate(environment)


__analyzer = PackageFileDependencyAnalyzer()


def analyze_package_deps(package_file_path: pathlib.Path) -> list[Requirement]:
    """分析包文件依赖项.

    Args:
        package_file_path (pathlib.Path): 包文件路径.

    Returns:
        list[Requirement]: 依赖项列表.
    """
    return __analyzer.analyze_dependencies(package_file_path)
