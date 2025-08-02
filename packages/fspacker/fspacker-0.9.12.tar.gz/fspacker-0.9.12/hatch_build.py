# hatch_build.py
from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
from functools import cached_property
from pathlib import Path
from time import perf_counter

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

logging.basicConfig(level=logging.INFO, format="[*] %(message)s")

CWD: Path = Path.cwd()
logger = logging.getLogger(__name__)


class CustomBuildHook(BuildHookInterface):
    """自定义构建钩子."""

    # 构建对象
    APP_NAME: str = "fsloader"

    # c源码路径
    SOURCE_DIR: Path = CWD / "fsloader"

    # 输出路径
    OUTPUT_DIR: Path = CWD / "src" / "fspacker" / "assets"

    @cached_property
    def is_windows(self) -> bool:
        """判断是否为Windows系统.

        Returns:
            bool: 是否为Windows系统
        """
        return platform.system() == "Windows"

    @cached_property
    def exe_files(self) -> list[str]:
        """获取可执行文件名列表.

        Returns:
            list[str]: 可执行文件名列表
        """
        modes = ["cli", "gui"]
        ext = ".exe" if self.is_windows else ""
        return [f"{self.APP_NAME}-{mode}{ext}" for mode in modes]

    @cached_property
    def app_dist_dir(self) -> Path:
        """获取可执行文件输出路径.

        Returns:
            Path: 可执行文件输出路径
        """
        if self.is_windows:
            return (
                self.SOURCE_DIR
                / "target"
                / "x86_64-win7-windows-msvc"
                / "release"
            )
        return self.SOURCE_DIR / "target" / "release"

    @cached_property
    def build_commands(self) -> list[list[str]]:
        """构建命令列表.

        Returns:
            list[list[str]]: 构建命令列表
        """
        if self.is_windows:
            return [
                ["rustup", "override", "set", "nightly-x86_64-pc-windows-msvc"],
                [
                    "rustup",
                    "component",
                    "add",
                    "rust-src",
                    "--toolchain",
                    "nightly-x86_64-pc-windows-msvc",
                ],
                [
                    "cargo",
                    "build",
                    "--release",
                    "-Z",
                    "build-std",
                    "--target",
                    "x86_64-win7-windows-msvc",
                    "--features",
                    "cli",
                ],
                [
                    "cargo",
                    "build",
                    "--release",
                    "-Z",
                    "build-std",
                    "--target",
                    "x86_64-win7-windows-msvc",
                    "--features",
                    "gui",
                ],
            ]
        return [
            [
                "cargo",
                "build",
                "--release",
                "-Z",
                "build-std",
                "--target",
                "x86_64-pc-linux-gnu",
                "--features",
                "cli",
            ],
            [
                "cargo",
                "build",
                "--release",
                "-Z",
                "build-std",
                "--target",
                "x86_64-pc-linux-gnu",
                "--features",
                "gui",
            ],
        ]

    def initialize(self, version: str, build_data: dict[str, str]) -> None:  # noqa: ARG002
        """初始化构建.

        Raises:
            SystemExit: 初始化失败.
        """
        if not self.is_windows:
            logger.info("非Windows系统, 跳过构建.")
            return

        t0 = perf_counter()

        if not self.OUTPUT_DIR.exists():
            self.OUTPUT_DIR.mkdir(parents=True)

        logger.info(
            f"启动构建, 名称: {self.APP_NAME}, \
                源码路径: {self.SOURCE_DIR}, \
                    输出路径: {self.OUTPUT_DIR}",
        )

        try:
            os.chdir(self.SOURCE_DIR)
            for command in self.build_commands:
                logger.info(f"运行编译命令: {command}")
                subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            msg = f"编译失败, 错误信息: {e}"
            raise SystemExit(msg) from e

        for exe_file in self.exe_files:
            app_dist_path = self.app_dist_dir / exe_file
            app_output_path = self.OUTPUT_DIR / exe_file
            if app_dist_path.exists():
                logger.info(f"拷贝文件: {app_dist_path} -> {app_output_path}")
                shutil.copyfile(app_dist_path, app_output_path)
            else:
                logger.error(f"未找到可执行文件, {app_dist_path}")

        logger.info(f"完成编译, 用时: {perf_counter() - t0:4f}s")
