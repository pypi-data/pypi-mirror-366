from __future__ import annotations

import logging
import platform
from pathlib import Path
from typing import Set

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from rich.logging import RichHandler

from fspacker import __build_date__
from fspacker import __version__
from fspacker.models.dirs import DEFAULT_CACHE_DIR
from fspacker.models.dirs import Dirs
from fspacker.models.mode import PackMode
from fspacker.models.urls import Urls

__all__ = ["get_settings"]

logger = logging.getLogger(__name__)

_env_filepath = DEFAULT_CACHE_DIR / ".env"
_export_prefixes = {"urls", "dirs"}


class Settings(BaseSettings):
    """Settings for fspacker."""

    model_config = SettingsConfigDict(
        env_file=str(_env_filepath),
        env_prefix="FSP_",
        env_nested_delimiter="__",
        extra="allow",
    )

    MAX_THREAD: int = 6

    is_windows: bool = platform.system() == "Windows"
    is_linux: bool = platform.system() == "Linux"
    is_macos: bool = platform.system() == "Darwin"

    dirs: Dirs = Dirs()
    urls: Urls = Urls()
    mode: PackMode = PackMode()

    src_dir: Path = Path(__file__).parent
    assets_dir: Path = src_dir / "assets"
    python_exe: str = (
        "python.exe" if platform.system() == "Windows" else "python3"
    )
    ignore_folders: Set[str] = {  # noqa: UP006
        "dist-info",
        "__pycache__",
        "site-packages",
        "runtime",
        "dist",
        ".venv",
    }
    # 窗口程序库
    gui_libs: Set[str] = {  # noqa: UP006
        "PySide2",
        "PyQt5",
        "pygame",
        "matplotlib",
        "tkinter",
        "pandas",
        "pywebview",
    }
    # 使用tk的库
    tk_libs: Set[str] = {"matplotlib", "tkinter", "pandas"}  # noqa: UP006
    # qt库
    qt_libs: Set[str] = {"PySide2", "PyQt5", "PySide6", "PyQt6"}  # noqa: UP006

    def show(self) -> None:
        logger.info(
            "[green bold]fspacker[/] 版本: "
            f"{__version__}, 构建日期: {__build_date__}",
        )
        logger.info(f"模式: {self.mode}")
        logger.info(f"链接: {self.urls}")
        logger.info(f"目录: {self.dirs}")

    def set_logger(self, *, debug: bool = False) -> None:
        level = logging.DEBUG if (debug or self.mode.debug) else logging.INFO

        logging.basicConfig(
            level=level,
            format="[*] %(message)s",
            datefmt="[%X]",
            handlers=[
                RichHandler(markup=True),
            ],
        )

    def dump(self) -> None:
        """导出环境变量."""
        prefix = self.model_config.get("env_prefix")

        with _env_filepath.open("w", encoding="utf-8") as f:
            for name, value in self.model_dump(by_alias=True).items():
                if str(name) in _export_prefixes:
                    if isinstance(value, dict):
                        for sub_key, sub_val in value.items():
                            env_name = f"{name.upper()}__{sub_key.upper()}"
                            f.write(f"{prefix}{env_name}={sub_val}\n")
                    else:
                        f.write(f"{prefix}{name.upper()}={value}\n")


_settings: Settings | None = None


def get_settings() -> Settings:
    """获取设置.

    Returns:
        Settings: 设置对象
    """
    global _settings  # noqa: PLW0603

    if _settings is None:
        _settings = Settings()

        for directory in _settings.dirs.entries:
            if not directory.exists():
                directory.mkdir(parents=True)

    return _settings
