from __future__ import annotations

from functools import cached_property

from pydantic import BaseModel

from fspacker.utils.url import get_fastest_url

_embed_url_prefixes: dict[str, str] = {
    "official": "https://www.python.org/ftp/python/",
    "huawei": "https://mirrors.huaweicloud.com/python/",
}

_pip_url_prefixes: dict[str, str] = {
    "aliyun": "https://mirrors.aliyun.com/pypi/simple/",
    "tsinghua": "https://pypi.tuna.tsinghua.edu.cn/simple/",
    "ustc": "https://pypi.mirrors.ustc.edu.cn/simple/",
    "huawei": "https://mirrors.huaweicloud.com/repository/pypi/simple/",
}


class Urls(BaseModel):
    """Url配置."""

    embed: str = ""
    pip: str = ""

    def __str__(self) -> str:
        """字符串化.

        Returns:
            str: 字符串值
        """
        return f"embed=[[green bold]{self.embed}[/]] \
            , pip=[[green bold]{self.pip}[/]]"

    @cached_property
    def fastest_pip_url(self) -> str:
        """从pip url列表中获取最快的url.

        Returns:
            str: 最快的url
        """
        self.pip = self.pip or get_fastest_url(_pip_url_prefixes)
        return self.pip

    @cached_property
    def fastest_embed_url(self) -> str:
        """从embed url列表中获取最快的url.

        Returns:
            str: 最快的url
        """
        self.embed = self.embed or get_fastest_url(_embed_url_prefixes)
        return self.embed
