import logging
import os
import platform
import shutil
import subprocess
from platform import machine

from fspacker.exceptions import ProjectPackError
from fspacker.exceptions import ResourceNotFoundError
from fspacker.packers._base import BasePacker
from fspacker.packers.factory import PackerFactory
from fspacker.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["NSISPortablePacker", "PostPacker"]


class PostPacker(BasePacker):
    NAME = "项目后处理打包"

    def pack(self) -> None:
        if get_settings().mode.archive:
            logger.info(f"压缩文件: [[green]{self.info.dist_dir}[/]]")
            shutil.make_archive(
                self.info.dist_dir.name,
                "zip",
                self.info.dist_dir.parent,
                self.info.dist_dir.name,
            )


class NSISPortablePacker(PostPacker):
    """NSIS打包工具, 用于Windows平台软件分发."""

    NAME = "NSIS打包工具"
    NSIS_ASSETS = get_settings().assets_dir / "nsis"
    NSIS_DIR = get_settings().dirs.tools / "nsis"
    NSIS_BUILD = NSIS_DIR / "build.nsi"
    NSIS_EXE = NSIS_DIR / "makensis.exe"
    NSIS_ICON = NSIS_ASSETS / "default.ico"
    RESOURCE_HACKER_EXE = get_settings().assets_dir / "ResourceHacker.exe"

    def setup(self) -> None:
        """NSIS打包工具初始化.

        Raises:
            ResourceNotFoundError: 找不到NSIS打包工具.
        """
        if not self.NSIS_ASSETS.exists():
            msg = f"找不到{self.NAME}: [[green]{self.NSIS_ASSETS}[/]]"
            raise ResourceNotFoundError(msg)

        if not self.NSIS_DIR.exists():
            logger.info(f"拷贝{self.NAME}: [[green]{self.NSIS_ASSETS}[/]]")
            shutil.copytree(self.NSIS_ASSETS, self.NSIS_DIR, dirs_exist_ok=True)
        else:
            logger.info(f"{self.NAME}已存在: [[green]{self.NSIS_DIR}[/]]")

        if not self.NSIS_EXE.exists():
            msg = f"找不到{self.NAME}: [[green]{self.NSIS_EXE}[/]]"
            raise ResourceNotFoundError(msg)

    def pack(self) -> None:
        """NSIS打包工具打包.

        Raises:
            ProjectPackError: 项目目录不存在.
        """
        if not get_settings().mode.archive:
            logger.info("非打包模式, 不执行NSIS打包")
            return

        # 处理图标
        self._make_exe_icon()
        shutil.copyfile(
            self.NSIS_ICON,
            self.info.dist_dir / "default.ico",
        )

        build_dir = self.info.project_dir / ".build"
        build_dir.mkdir(parents=True, exist_ok=True)
        build_nsis = build_dir / "build.nsi"

        try:
            # 复制NSIS脚本
            shutil.copyfile(self.NSIS_BUILD, build_nsis)
        except Exception as e:
            msg = "复制文件失败"
            raise ProjectPackError(msg) from e

        nsis_params = {
            "APPDIR": r"..\\dist",
            "FILENAME": self.info.normalized_name,
            "APPNAME": self.info.normalized_name,
            "VERSION": self.info.version,
            "AUTHOR": self.info.authors[0] if self.info.authors else "Unknown",
            "PUBLISHER": "",
            "DESCRIPTION": self.info.description,
            "ICON": str(self.NSIS_ICON),
            "LICENSE": self.info.license_file or "",
            "INSTALLSIZE": self._calc_install_size(),
            "ARCH": str(machine()),
        }

        for key, value in nsis_params.items():
            build_file = build_dir / key
            with build_file.open("w", encoding="utf-8") as f:
                f.write(str(value))

        os.chdir(str(self.info.project_dir))
        commands = [str(self.NSIS_EXE), str(build_nsis)]
        logger.info(f"NSIS打包: [[green]{commands}[/]]")
        try:
            subprocess.run(commands, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            msg = "NSIS打包失败"
            raise ProjectPackError(msg) from e
        else:
            packed = next(build_dir.glob("*.exe"))
            logger.info(f"打包完成: [[green]{packed}[/]]")

    def _calc_install_size(self) -> int:
        """计算安装包大小.

        Returns:
            int: 安装包大小, 单位为MB.

        Raises:
            ProjectPackError: 计算安装包大小失败.
        """
        if not self.info.dist_dir.exists():
            msg = f"找不到[[green]{self.info.dist_dir}[/]]"
            raise ProjectPackError(msg)

        files = self.info.dist_dir.glob("**/*")
        size = 0
        for file in files:
            size += file.stat().st_size // 1024 // 1024

        return size

    def _make_exe_icon(self) -> None:
        """植入图标文件.

        Raises:
            ResourceNotFoundError: 找不到ResourceHacker.exe.
            ProjectPackError: 植入图标文件失败.
        """
        if not self.RESOURCE_HACKER_EXE.exists():
            msg = f"找不到 [[red]{self.RESOURCE_HACKER_EXE}[/]]"
            raise ResourceNotFoundError(msg)

        commands = [
            str(self.RESOURCE_HACKER_EXE),
            "-open",
            str(self.info.exe_file),
            "-save",
            str(self.info.exe_file),
            "-action",
            "addoverwrite",
            "-res",
            str(self.NSIS_ICON),
            "-mask",
            "ICONGROUP,MAINICON,0",
        ]
        logger.info(f"植入图标文件: [[green]{commands}[/]]")
        try:
            subprocess.run(commands, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            msg = "植入图标文件失败"
            raise ProjectPackError(msg) from e
        else:
            logger.info(f"图标文件植入成功: [[green]{self.info.exe_file}[/]]")


def get_post_packer(parent: PackerFactory) -> PostPacker:
    if platform.system() == "Windows":
        return NSISPortablePacker(parent)
    return PostPacker(parent)
