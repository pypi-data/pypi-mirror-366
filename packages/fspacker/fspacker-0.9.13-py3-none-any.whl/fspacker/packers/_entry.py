import logging
import platform
import shutil
import string

from fspacker.packers._base import BasePacker
from fspacker.settings import get_settings

logger = logging.getLogger(__name__)

_init_script = """
import os
import site
import sys
from pathlib import Path

# setup env
cwd = Path.cwd()
site_dirs = [cwd / "site-packages", cwd / "lib"]
dirs = [cwd, cwd / "src", cwd / "runtime", *site_dirs]

for dir in dirs:
    sys.path.append(str(dir))

for dir in site_dirs:
    site.addsitedir(str(dir))
"""

# int file template
INT_TEMPLATE = string.Template(
    """\
$INIT_SCRIPT

# main
from $SRC import main
main()
""",
)

INT_TEMPLATE_QT = string.Template(
    """\
$INIT_SCRIPT

# for qt
import $LIB_NAME
qt_dir = os.path.dirname($LIB_NAME.__file__)
plugin_path = os.path.join(qt_dir, "plugins" , "platforms")
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path

# main
from $SRC import main
main()
""",
)


class EntryPacker(BasePacker):
    NAME = "入口程序打包"

    def pack(self) -> None:
        name = self.info.normalized_name

        if not self.info.source_file or not self.info.source_file.exists():
            logger.error(f"入口文件{self.info.source_file}无效")
            return

        if self.info.is_normal_project:
            source = f"{self.info.normalized_name}.{self.info.source_file.stem}"
        else:
            source = self.info.source_file.stem

        ext = ".exe" if platform.system() == "Windows" else ""
        mode = (
            "gui"
            if self.info.is_gui and not get_settings().mode.debug
            else "cli"
        )
        exe_filename = f"fsloader-{mode}{ext}"
        src_exe_path = get_settings().assets_dir / exe_filename
        dst_exe_path = self.info.dist_dir / f"{name}.exe"

        logger.info(
            f"打包目标类型: {'[green bold]窗口' if self.info.is_gui else '[red bold]控制台'}[/]",  # noqa: E501
        )
        logger.info(
            f"复制可执行文件: [green underline]{src_exe_path.name} -> "
            f"{dst_exe_path.relative_to(self.info.project_dir)}[/]"
            f"[bold green]:heavy_check_mark:",
        )

        if src_exe_path.exists():
            try:
                shutil.copy(src_exe_path, dst_exe_path)
            except OSError:
                logger.exception("复制文件失败.")
        else:
            logger.error(f"可执行文件 {src_exe_path} 不存在, 跳过.")

        dst_int_path = self.info.dist_dir / f"{name}.int"
        logger.info(
            f"创建 int 文件: [green underline]{name}.int -> "
            f"{dst_int_path.relative_to(self.info.project_dir)}"
            f"[/] [bold green]:heavy_check_mark:",
        )

        for lib_name in get_settings().qt_libs:
            if lib_name in self.info.ast_modules:
                logger.info(f"检测到目标库: {lib_name}")
                content = INT_TEMPLATE_QT.substitute(
                    INIT_SCRIPT=_init_script,
                    SRC=f"src.{source}",
                    LIB_NAME=lib_name,
                )
                break
        else:
            content = INT_TEMPLATE.substitute(
                INIT_SCRIPT=_init_script,
                SRC=f"src.{source}",
            )

        with dst_int_path.open("w", encoding="utf-8") as f:
            f.write(content)
