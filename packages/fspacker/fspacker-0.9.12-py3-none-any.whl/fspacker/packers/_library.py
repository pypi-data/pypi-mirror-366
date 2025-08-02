from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar

from packaging.requirements import Requirement

from fspacker.packers._base import BasePacker
from fspacker.parsers.package import analyze_package_deps
from fspacker.settings import get_settings
from fspacker.utils.package import download_to_libs_dir
from fspacker.utils.package import get_cached_package
from fspacker.utils.package import install_package
from fspacker.utils.requirement import RequirementParser

logger = logging.getLogger(__name__)


class LibraryPacker(BasePacker):
    NAME = "依赖库打包"

    # 已打包的库
    packed_libs: ClassVar[set] = set()

    def _install_lib(self, req: Requirement) -> Path | None:
        dist_dir = self.info.dist_dir / "site-packages"
        dist_dir.mkdir(parents=True, exist_ok=True)

        if req.name.lower() in self.packed_libs:
            logger.info(f"已存在库: [[green bold]{req.name}[/]]")
            return None

        logger.info(f"打包依赖: [[green bold]{req}[/]]")
        cached_file = get_cached_package(req)
        if cached_file:
            logger.info(f"找到本地满足要求的依赖: [[green]{cached_file.name}]")
        else:
            logger.info(f"下载依赖: [[green]{req}[/]]")
            cached_file = download_to_libs_dir(req)

        if cached_file.is_file():
            logger.info(f"安装依赖: [[green]{cached_file.name}[/]]")
            install_package(
                req,
                cached_file,
                dist_dir,
                simplify=get_settings().mode.simplify,
            )
            self.packed_libs.add(req.name.lower())
            return cached_file
        logger.error(f"处理依赖失败: [[red bold]{req}[/]]")
        return None

    def pack(self) -> None:
        """打包依赖库."""
        logger.info(f"分析一级依赖库: [[green bold]{self.dependencies}[/]]")
        for top_req in self.dependencies:
            req = RequirementParser.parse(top_req)
            if not req:
                logger.error(f"解析依赖失败: [[red bold]{top_req}[/]]")
                continue

            logger.info(f"打包顶层依赖: [[green bold]{req}[/]]")
            cached_file = self._install_lib(req)
            if cached_file:
                secondary_reqs = analyze_package_deps(cached_file)
                logger.info(f"分析二级依赖: [[green]{secondary_reqs}[/]]")
                for secondary_req in secondary_reqs:
                    self._install_lib(secondary_req)
