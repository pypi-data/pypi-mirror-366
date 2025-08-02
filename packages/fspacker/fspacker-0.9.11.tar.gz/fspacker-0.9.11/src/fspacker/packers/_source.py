import logging
import re
import shutil
from pathlib import Path

from fspacker.packers._base import BasePacker

logger = logging.getLogger(__name__)


class SourceResPacker(BasePacker):
    NAME = "源码 & 资源打包"

    # 忽视清单
    IGNORE_ENTRIES = frozenset([
        "dist-info",
        "site-packages",
        "runtime",
        "dist",
    ])

    def is_valid_entry(self, filepath: Path) -> bool:
        """判断文件是否有效.

        Args:
            filepath: 文件路径.

        Returns:
            是否有效.
        """
        return all(x not in str(filepath) for x in self.IGNORE_ENTRIES) and all(
            not filepath.stem.startswith(_) for _ in list("._")
        )

    def pack(self) -> None:
        if not self.info.project_dir:
            logger.error("项目文件夹不存在")
            return

        if not self.info.normalized_dir:
            logger.error(f"项目文件夹不存在: {self.info.normalized_dir}")
            return

        if self.info.is_normal_project:
            # 常规项目结构: `pyproject.toml / src / project_name`
            dest_dir = self.info.dist_dir / "src" / self.info.normalized_name
            source_files = [
                file
                for file in self.info.normalized_dir.glob("*.py")
                if self.is_valid_entry(file)
            ]
        else:
            # 非常规项目结构
            dest_dir = self.info.dist_dir / "src"
            source_files = [
                file
                for file in self.info.project_dir.rglob("*.py")
                if self.is_valid_entry(file)
            ]

        logger.debug(f"目标文件夹: [green bold]{dest_dir}")

        pattern = re.compile(
            # 匹配def main
            r"(def\s+main\s*$.*?$\s*:)|"
            # 匹配if __name__...
            r'(if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:)',
            flags=re.MULTILINE | re.DOTALL,
        )

        for source_file in source_files:
            with source_file.open(encoding="utf8") as f:
                content = "\n".join(f.readlines())
            matches = pattern.findall(content)
            if len(matches):
                logger.info(
                    f"入口 Python 文件: [[green bold]{source_file}[/]]",
                )
                self.info.source_file = source_file
                source_folder = source_file.absolute().parent
                break
        else:
            logger.error("未找到入口 Python 文件")
            return

        dest_dir.mkdir(parents=True, exist_ok=True)
        for entry in source_folder.iterdir():
            dest_path = dest_dir / entry.name

            # 不拷贝pyproject.toml文件
            if entry.is_file() and entry.name != "pyproject.toml":
                logger.info(
                    f"复制目标文件: [green underline]{entry.name}[/]"
                    f" [bold green]:heavy_check_mark:",
                )
                shutil.copy2(entry, dest_path)
            elif entry.is_dir():
                if self.is_valid_entry(entry):
                    logger.info(
                        f"复制目标文件夹: [purple underline]{entry.name}[/]"
                        " [bold purple]:heavy_check_mark:",
                    )
                    shutil.copytree(entry, dest_path, dirs_exist_ok=True)
                else:
                    logger.info(f"跳过文件夹 [red]{entry.name}")
