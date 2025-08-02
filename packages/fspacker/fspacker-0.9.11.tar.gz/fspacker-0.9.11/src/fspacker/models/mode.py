from pydantic import BaseModel

__all__ = ["PackMode"]

_pack_modes = {
    "archive": ("", "压缩"),
    "debug": ("非调试", "调试"),
    "gui": ("CONSOLE", "GUI"),
    "offline": ("在线", "离线"),
    "rebuild": ("", "重构"),
    "recursive": ("", "递归"),
    "simplify": ("", "简化"),
    "use_tk": ("", "tk"),
}


class PackMode(BaseModel):
    """打包模式信息."""

    archive: bool = False
    debug: bool = False
    gui: bool = False
    offline: bool = False
    rebuild: bool = False
    recursive: bool = False
    simplify: bool = False
    use_tk: bool = False

    def __str__(self) -> str:
        """返回打包模式字符串.

        Returns:
            str: 打包模式字符串.
        """
        mode_str = []
        for k, v in self.__dict__.items():
            if k in _pack_modes:
                prefix = "[red bold]" if int(v) else "[green bold]"
                val = _pack_modes.get(k, "")[int(v)]
                if val:
                    mode_str.append(prefix + val + "[/]")
        return ", ".join(mode_str)

    def reset(self) -> None:
        """重置打包模式."""
        self.archive = False
        self.debug = False
        self.gui = False
        self.offline = False
        self.rebuild = False
        self.recursive = False
        self.simplify = False
        self.use_tk = False
