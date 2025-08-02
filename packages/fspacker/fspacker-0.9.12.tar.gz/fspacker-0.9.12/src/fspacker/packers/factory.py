import logging
import time

__all__ = ["PackerFactory"]

from fspacker.exceptions import ProjectPackError
from fspacker.parsers.project import Project
from fspacker.settings import get_settings

logger = logging.getLogger(__name__)


class PackerFactory:
    """打包工具."""

    def __init__(self, info: Project) -> None:
        from fspacker.packers._base import BasePacker  # noqa: PLC0415
        from fspacker.packers._builtins import BuiltinsPacker  # noqa: PLC0415
        from fspacker.packers._entry import EntryPacker  # noqa: PLC0415
        from fspacker.packers._library import LibraryPacker  # noqa: PLC0415
        from fspacker.packers._post import get_post_packer  # noqa: PLC0415
        from fspacker.packers._pre import PrePacker  # noqa: PLC0415
        from fspacker.packers._runtime import RuntimePacker  # noqa: PLC0415
        from fspacker.packers._source import SourceResPacker  # noqa: PLC0415

        self.info: Project = info

        # 打包器集合, 注意打包顺序
        self.packers: list[BasePacker] = [
            PrePacker(self),
            SourceResPacker(self),
            LibraryPacker(self),
            BuiltinsPacker(self),
            EntryPacker(self),
            RuntimePacker(self),
            get_post_packer(self),
        ]

    def setup(self) -> None:
        """初始化打包工具."""
        for packer in self.packers:
            if packer:
                logger.info(f"初始化打包工具: {packer}")
                packer.setup()

    def pack(self) -> None:
        """打包项目."""
        logger.info(f"{'*' * 80}")
        logger.info(
            f"启动构建, 源码根目录: [[green underline]\
                {self.info.project_dir}[/]]",
        )
        t0 = time.perf_counter()

        try:
            for packer in self.packers:
                if packer:
                    logger.info(f"启动打包: {packer}")
                    packer.pack()

        except ProjectPackError:
            logger.exception(
                f"项目打包出错: [red bold]{self.info.normalized_name}",
            )
            return

        logger.info(f"打包完成! 总用时: [{time.perf_counter() - t0:.4f}]s.")
        if not get_settings().mode.debug:
            logger.info(f"{'*' * 80}")
