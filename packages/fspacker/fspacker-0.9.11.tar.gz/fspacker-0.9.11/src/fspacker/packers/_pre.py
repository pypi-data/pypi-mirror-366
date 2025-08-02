import logging
import shutil

from fspacker.packers._base import BasePacker
from fspacker.settings import get_settings

logger = logging.getLogger(__name__)


class PrePacker(BasePacker):
    NAME = "项目初始化打包"

    def pack(self) -> None:
        if get_settings().mode.rebuild:
            logger.info(f"清理旧文件: [[green]{self.info.dist_dir}[/]]")
            shutil.rmtree(self.info.dist_dir, ignore_errors=True)

        for directory in (self.info.dist_dir,):
            logger.info(f"创建文件夹: [[purple]{directory.name}[/]]")
            directory.mkdir(parents=True, exist_ok=True)
