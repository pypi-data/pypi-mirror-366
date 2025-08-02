from __future__ import annotations

import logging
import time
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


class ParseUrlError(ValueError):
    """解析 url 失败."""


def check_url_access_time(url: str) -> float:
    """测试 url 访问时间.

    Args:
        url: 待访问的 url.

    Returns:
        访问时间, 单位: 秒.
    """
    start = time.perf_counter()
    try:
        response = requests.get(url, timeout=2)
        response.raise_for_status()
        time_used = time.perf_counter() - start
        logger.info(
            f"地址 [[green]{url}[/]] 访问时间: [green] {time_used:.2f}s",
        )
    except requests.exceptions.RequestException:
        logger.info(f"地址 [[red bold]{url}[/]] 访问超时")
        return -1
    else:
        return time_used


def get_fastest_url(urls: dict[str, str]) -> str:
    """从给定的URL字典中找出访问速度最快的链接。.

    Args:
        urls: 包含多个URL的字典, 格式为 {名称: URL}

    Returns:
        访问速度最快的URL字符串

    Note:
        如果所有URL都无法访问, 将返回空字符串
    """
    """获取 Embed python 最快访问链接地址."""
    min_time, fastest_url = 10.0, ""
    for embed_url in urls.values():
        time_used = check_url_access_time(embed_url)
        if time_used > 0 and time_used < min_time:
            fastest_url = embed_url
            min_time = time_used

    logger.info(f"找到最快地址: [[green bold]{fastest_url}[/]]")
    return fastest_url


def validate_url_scheme(url: str, allowed_schemes: set[str]) -> None:
    """验证URL scheme是否被允许.

    Args:
        url: 待验证的URL
        allowed_schemes: 允许的scheme集合

    Raises:
        ParseUrlError: 如果scheme不被允许
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme not in allowed_schemes:
        msg = f"不支持的 URL scheme: {parsed_url.scheme}"
        raise ParseUrlError(msg)


def safe_read_url_data(url: str, timeout: int = 10) -> bytes | None:
    """读取 url 数据.

    Args:
        url: 待读取的 url.
        timeout: 超时时间, 单位: 秒.

    Returns:
        读取到的数据, 如果读取失败, 返回 None.

    Raises:
        ParseUrlError: 如果 scheme 不被允许
    """
    try:
        validate_url_scheme(url, allowed_schemes={"https"})
    except ParseUrlError:
        logger.exception("不支持的 URL scheme")
        return None

    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.ConnectionError as e:
        msg = "读取URL失败"
        raise ParseUrlError(msg) from e
    except requests.exceptions.Timeout as e:
        msg = "读取URL超时"
        raise ParseUrlError(msg) from e
    except Exception as e:
        msg = "读取URL失败"
        raise ParseUrlError(msg) from e
    else:
        logger.info(f"读取URL成功: {url}")
        return response.content
