import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def calc_checksum(filepath: Path, block_size: int = 4096) -> str:
    """计算文件校验和.

    Args:
        filepath (Path): 文件路径.
        block_size (int, optional): 读取文件块大小. Defaults to 4096.

    Returns:
        str: 校验和.
    """
    hash_method = hashlib.sha256()
    logger.info(
        f"计算文件校验和: [green underline]{filepath.name}"
        f"[/] [bold green]:heavy_check_mark:",
    )

    try:
        with filepath.open("rb") as file:
            for chunk in iter(lambda: file.read(block_size), b""):
                hash_method.update(chunk)

    except FileNotFoundError:
        logger.exception(
            f"文件不存在: [red underline]{filepath}[/] "
            f"[bold red]:white_exclamation_mark:",
        )
        return ""
    except OSError:
        logger.exception(
            f"读取文件 IO 错误: [red underline]{filepath}[/], "
            f"[bold red]:white_exclamation_mark:",
        )
        return ""

    checksum = hash_method.hexdigest()
    logger.debug(
        f"校验和计算值: [green underline]{checksum}[/] "
        f"[bold green]:heavy_check_mark:",
    )
    return checksum
