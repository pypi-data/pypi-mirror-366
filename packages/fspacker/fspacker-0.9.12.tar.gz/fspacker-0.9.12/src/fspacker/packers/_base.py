from __future__ import annotations

from fspacker.packers.factory import PackerFactory
from fspacker.parsers.project import Project


class BasePacker:
    """针对特定场景打包工具."""

    NAME = "基础打包"

    def __init__(self, parent: PackerFactory) -> None:
        self.parent = parent

    def __repr__(self) -> str:
        """字符串表示.

        Returns:
            str: 打包工具名称.
        """
        return f"[[green]{self.NAME} - {self.__class__.__name__}[/]]"

    @property
    def info(self) -> Project:
        """返回项目信息.

        Returns:
            Project: 项目信息.
        """
        return self.parent.info

    @property
    def dependencies(self) -> list[str]:
        """返回打包工具依赖的库.

        Returns:
            list[str]: 依赖的库列表.
        """
        return self.info.dependencies

    def setup(self) -> None:
        """初始化打包工具."""

    def pack(self) -> None:
        """打包."""
