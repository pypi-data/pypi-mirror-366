import logging
import shutil

from fspacker.packers._base import BasePacker

logger = logging.getLogger(__name__)


class SourceResPacker(BasePacker):
    NAME = "源码 & 资源打包"

    def pack(self) -> None:
        if not self.info.normalized_dir:
            logger.error(f"项目文件夹不存在: {self.info.normalized_dir}")
            return

        if not self.info.source_file:
            logger.error(f"源文件不存在: {self.info.source_file}")
            return

        logger.debug(f"目标文件夹: [green bold]{self.info.dest_src_dir}")
        self.info.dest_src_dir.mkdir(parents=True, exist_ok=True)

        source_folder = self.info.source_file.absolute().parent
        for entry in source_folder.iterdir():
            dest_path = self.info.dest_src_dir / entry.name

            # 不拷贝pyproject.toml文件
            if entry.is_file() and entry.name != "pyproject.toml":
                logger.info(
                    f"复制目标文件: [green underline]{entry.name}[/]"
                    f" [bold green]:heavy_check_mark:",
                )
                shutil.copy2(entry, dest_path)
            elif entry.is_dir():
                if self.info.is_valid_entry(entry):
                    logger.info(
                        f"复制目标文件夹: [purple underline]{entry.name}[/]"
                        " [bold purple]:heavy_check_mark:",
                    )
                    shutil.copytree(entry, dest_path, dirs_exist_ok=True)
                else:
                    logger.info(f"跳过文件夹 [red]{entry.name}")
