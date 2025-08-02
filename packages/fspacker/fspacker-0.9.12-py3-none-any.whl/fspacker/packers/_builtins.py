import logging
import shutil

from fspacker.packers._base import BasePacker
from fspacker.settings import get_settings

logger = logging.getLogger(__name__)


class BuiltinsPacker(BasePacker):
    NAME = "内置依赖库打包"

    def pack(self) -> None:
        # 显式声明 use_tk 模式, 或者存在使用 tkinter 的相关依赖
        intersect_libs = bool(self.info.ast_modules & get_settings().tk_libs)

        if intersect_libs:
            logger.info(f"检测到 tkinter 相关依赖: [green]{intersect_libs}")

        if get_settings().mode.use_tk or intersect_libs:
            tk_lib = get_settings().assets_dir / "tkinter-lib.zip"
            tk_package = get_settings().assets_dir / "tkinter.zip"
            logger.info(f"解压tk文件: [green]{tk_lib}[/], [green]{tk_package}")
            shutil.unpack_archive(tk_lib, self.info.dist_dir, "zip")
            shutil.unpack_archive(
                tk_package,
                self.info.dist_dir / "site-packages",
                "zip",
            )
