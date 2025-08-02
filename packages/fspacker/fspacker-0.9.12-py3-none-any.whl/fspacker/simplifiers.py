"""提供库打包精简配置功能."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "get_simplify_options",
]


@dataclass
class SimplifierOption:
    """库简化打包配置."""

    # 白名单匹配规则
    patterns: set[str] | None = None

    # 黑名单匹配规则
    excludes: set[str] | None = None


# 简化配置
_simplifier_options_dict: dict[str, SimplifierOption] = {
    "matplotlib": SimplifierOption(
        excludes={"matplotlib-.*.pth"},
        patterns={
            "matplotlib/*",
            "matplotlib.libs/*",
            "mpl_toolkits/*",
            "pylab.py",
        },
    ),
    "numba": SimplifierOption(
        patterns={
            "numba/*",
            "numba*data/*",
        },
    ),
    "numpy": SimplifierOption(
        excludes={
            "numpy/_pyinstaller/*",
            "numpy/tests/*",
        },
    ),
    "pygame": SimplifierOption(
        excludes={
            "pygame/docs/*",
            "pygame/examples/*",
            "pygame/tests/*",
            "pygame/__pyinstaller/*",
            "pygame*data/*",
        },
    ),
    "pyqt5": SimplifierOption(
        patterns={
            "PyQt5/__init__.py",
            "PyQt5/QtCore.pyd",
            "PyQt5/QtGui.pyd",
            "PyQt5/QtWidgets.pyd",
            "PyQt5/QtNetwork.pyd",
            "PyQt5/QtQml.pyd",
            "PyQt5/Qt/bin/Qt5Core.dll",
            "PyQt5/Qt/bin/Qt5Gui.dll",
            "PyQt5/Qt/bin/Qt5Widgets.dll",
            "PyQt5/Qt/bin/Qt5Network.dll",
            "PyQt5/Qt/bin/Qt5Qml.dll",
            "*plugins/iconengines/qsvgicon.dll",
            "*plugins/imageformats/*.dll",
            "*plugins/platforms/*.dll",
            # linux
            "PyQt5/QtCore.abi3.so",
            "PyQt5/QtGui.abi3.so",
            "PyQt5/QtWidgets.abi3.so",
            "PyQt5/QtNetwork.abi3.so",
            "PyQt5/QtQml.abi3.so",
            "*plugins/iconengines/libqsvgicon.so",
            "*plugins/imageformats/*.so",
            "*plugins/platforms/*.so",
        },
    ),
    "pyside2": SimplifierOption(
        patterns={
            "PySide2/__init__.py",
            # windows
            "PySide2/pyside2.abi3.dll",
            "PySide2/QtCore.pyd",
            "PySide2/Qt5Core.dll",
            "PySide2/QtGui.pyd",
            "PySide2/Qt5Gui.dll",
            "PySide2/QtWidgets.pyd",
            "PySide2/Qt5Widgets.dll",
            "PySide2/QtNetwork.pyd",
            "PySide2/Qt5Network.dll",
            "PySide2/QtQml.pyd",
            "PySide2/Qt5Qml.dll",
            "*plugins/iconengines/qsvgicon.dll",
            "*plugins/imageformats/*.dll",
            "*plugins/platforms/*.dll",
            # linux
            "PySide2/libpyside2.abi3.so",
            "PySide2/QtCore.abi3.so",
            "PySide2/QtGui.abi3.so",
            "PySide2/QtWidgets.abi3.so",
            "PySide2/QtNetwork.abi3.so",
            "PySide2/QtQml.abi3.so",
            "*plugins/iconengines/libqsvgicon.so",
            "*plugins/imageformats/*.so",
            "*plugins/platforms/*.so",
        },
    ),
    "torch": SimplifierOption(
        excludes={
            # for debug
            "torch/utils/bottleneck/*",
            "torch/utils/checkpoint/*",
            "torch/utils/tensorboard/*",
            # for test
            "torch/utils/data/dataset/*",
            "torch/utils/data/dataloader/*",
        },
    ),
}


def get_simplify_options(name: str) -> SimplifierOption | None:
    """获取库打包精简配置.

    Args:
        name (str): 库名称

    Returns:
        SimplifierOption: 库打包精简配置
    """
    return _simplifier_options_dict.get(name.lower(), None)
