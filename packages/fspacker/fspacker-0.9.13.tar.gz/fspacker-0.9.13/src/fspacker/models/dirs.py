from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

__all__ = ["DEFAULT_CACHE_DIR", "Dirs"]

# cache settings
DEFAULT_CACHE_DIR = Path("~").expanduser() / ".cache" / "fspacker"


class Dirs(BaseModel):
    """目录配置."""

    cache: Path = DEFAULT_CACHE_DIR
    embed: Path = cache / "embed-repo"
    libs: Path = cache / "libs-repo"
    tools: Path = cache / "tools"
    checksum: str = ""

    def __str__(self) -> str:
        """字符串化.

        Returns:
            str: 字符串.
        """
        return f"cache={self.cache}, embed={self.embed},\
            libs={self.libs}, tools={self.tools}"

    @property
    def entries(self) -> tuple[Path, Path, Path]:
        """获取所有目录.

        Returns:
            tuple[Path, Path, Path]: 所有目录
        """
        return (self.cache, self.embed, self.libs)
