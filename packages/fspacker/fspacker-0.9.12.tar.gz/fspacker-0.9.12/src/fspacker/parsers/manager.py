from __future__ import annotations

import logging
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fspacker.exceptions import ProjectParseError
from fspacker.exceptions import RunExecutableError
from fspacker.packers.factory import PackerFactory
from fspacker.parsers.project import Project
from fspacker.settings import get_settings
from fspacker.trackers import perf_tracker

logger = logging.getLogger(__name__)


class ProjectManager:
    """项目管理工具, 可执行搜索、构建、运行、清理等操作."""

    def __init__(
        self,
        root_dir: str | Path = ".",
        match_name: str = "",
    ) -> None:
        self.projects: set[Project] = set()
        if match_name:
            entries = [
                d for d in Path(root_dir).iterdir() if match_name in d.stem
            ]
            if entries:
                self.root_dir = entries[0]
            else:
                logger.warning(
                    f"未找到匹配项目: {match_name}, "
                    f"退回解析根目录: {Path(root_dir)}",
                )
                self.root_dir = Path(root_dir)
        else:
            self.root_dir = Path(root_dir)

        # 分析根目录下的所有项目
        self._parse_projects()

    @perf_tracker
    def build(self) -> None:
        """构建项目."""
        with ThreadPoolExecutor(max_workers=get_settings().MAX_THREAD) as e:
            for project in self.projects:
                e.submit(PackerFactory(info=project).setup)
                e.submit(PackerFactory(info=project).pack)

    @perf_tracker
    def run(self, name: str = "") -> None:
        """运行项目.

        Raises:
            RunExecutableError: 未找到项目或可执行文件
        """
        if len(self.projects) > 1:
            if not name:
                msg = f"存在多个项目, 请输入名称: \
                    {[p.name for p in self.projects]}"
                raise RunExecutableError(msg)

            project_run = [
                p
                for p in self.projects
                if name.lower() in p.normalized_name.lower()
            ]
            if project_run:
                project_run = project_run[0]
            else:
                msg = f"未找到项目: {name}"
                raise RunExecutableError(msg)
        else:
            project_run = next(iter(self.projects))

        if not project_run.exe_file.exists():
            msg = f"项目可执行文件不存在: {project_run}"
            raise RunExecutableError(msg)

        logger.info(f"调用可执行文件: [green bold]{project_run.exe_file}")
        logger.info(f"[red]{'*' * 40} 执行信息 {'*' * 40}")
        os.chdir(project_run.dist_dir)
        subprocess.call(str(project_run.exe_file), shell=False)

    @perf_tracker
    def clean(self) -> None:
        """清理项目分发目录."""
        with ThreadPoolExecutor(max_workers=get_settings().MAX_THREAD) as e:
            for project in self.projects:
                build_dir = project.project_dir / ".build"
                if build_dir.exists():
                    logger.info(f"删除 .build 目录: {build_dir}")
                    e.submit(shutil.rmtree, build_dir)

                if project.dist_dir.exists():
                    logger.info(f"删除 dist 目录: {project.dist_dir}")
                    e.submit(shutil.rmtree, project.dist_dir)

    def _parse_projects(self) -> None:
        if not self.root_dir.exists():
            msg = f"根目录无效: {self.root_dir}"
            raise ProjectParseError(msg)

        # 递归搜索模式
        if get_settings().mode.recursive:
            directories = [
                entry for entry in self.root_dir.iterdir() if entry.is_dir()
            ]
            with ThreadPoolExecutor(
                max_workers=get_settings().MAX_THREAD,
            ) as e:
                for directory in directories:
                    logger.debug(f"搜索子目录: {directory}")
                    e.submit(self._parse_child_dir, directory)

        self._parse_child_dir(self.root_dir)
        if not self.projects:
            msg = f"路径下未找到有效的 pyproject.toml 文件: {self.root_dir}"
            raise ProjectParseError(msg)

        logger.info(f"已解析项目: [green bold]{self.projects}")

    def _parse_child_dir(self, directory: Path) -> None:
        """Parse `pyproject.toml` files in the given directory recursively."""
        for root, dirs, files in os.walk(str(directory)):
            dirs[:] = list(set(dirs) - get_settings().ignore_folders)
            for file in files:
                filepath = Path(root) / file
                if filepath.name == "pyproject.toml":
                    project = Project(filepath.parent)
                    if project.name:
                        logger.debug(f"找到有效项目, {project}")
                        self.projects.add(project)
