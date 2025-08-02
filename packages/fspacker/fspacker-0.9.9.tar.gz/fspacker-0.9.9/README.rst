##############
FSPacker
##############

Python **极简** 打包工具集. 👉️ `在线文档`_

.. image:: _static/demo.gif
   :align: center
   :alt: demo

.. _在线文档: https://fspacker.readthedocs.io/zh-cn/latest/

=============
🚀 关键特性
=============

-------------
✅️ 已实现
-------------

* ⚡️ **极速打包**: 比 ``PyInstaller``、 ``Nuitka`` 等现有库打包速度快10-100倍

* 🔧 **操作便捷**: 支持打包、清理、运行等多种模式

* ✨ **多项部署**: 支持批量打包多个应用

* 🌐 **离线模式**: 支持离线打包

* 📦️ **压缩模式**: 支持 ``zip`` 格式压缩打包

--------------
⏳ 开发中
--------------

* 📦️ **分发部署**: 支持生成 ``innosetup`` 安装包 :sub:`计划: v0.9.2`

* 🕙️ **性能优化**: 支持 ``nuitka`` 编译, 优化瓶颈部分代码 :sub:`计划: v0.9.3`

* 🛡️ **加密防护**: 支持 ``pyarmor`` 加密 :sub:`计划: v0.9.4`

=============
💻️ 支持平台
=============

- ✅ Windows 7 ~ 11
- ⏳ Linux :sub:`计划: v0.9.6`
- ❌️ MacOS :sub:`暂不支持`

=============
📚️ 支持库
=============

- ✅ tkinter ``windows``
- ✅ pyside2
- ✅ pyqt5
- ⏳ pyside6 :sub:`计划: v0.9.1`
- ✅ matplotlib
- ✅ pandas
- ✅ pytorch

=============
📖 快速入门
=============

使用方式:

.. code-block:: bash

    pip install fspacker
    cd dir/of/pyproject.toml
    fsp b

.. warning::

    - 项目必须包含 ``pyproject.toml`` 配置文件, 可使用 ``uv`` 或者 ``poetry`` 生成

    - 项目必须包含作为程序入口的 ``def main():`` 函数, 或者 ``if __name__ == "__main__:"`` 入口函数

Python项目结构:

.. code-block:: bash

    ex01_helloworld/
    |
    |___ core
    |   |____ __init__.py
    |   |____ core_a.py
    |   |____ core_b.py
    |   |____ core_c.py
    |
    |___ mathtools/
    |   |____ __init__.py
    |   |____ algorithms.py
    |
    |___ modules/
    |   |____ __init__.py
    |   |____ mod_a.py
    |   |____ mod_b.py
    |
    |___ ex01_helloworld.py
    |___ global_a.py
    |___ global_b.py
    |___ pyproject.toml

代码示例:

.. code-block:: python

    # ex01_helloworld.py
    import global_a  # import
    import global_b
    from modules.mod_a import function_mod_a  # import from
    from modules.mod_b import function_mod_b  # import from

    def main():
        print("hello, world")

        function_mod_a()
        function_mod_b()
        global_a.function_global_a()
        global_b.function_global_b()

    if __name__ == "__main__":
        main()

生成文件:

.. code-block:: bash

    ex01_helloworld/
    |
    |___ ...
    |
    |___ dist/
    |   |____ runtime/
    |   |     |___... # embed python 文件
    |   |
    |   |____ site-packages/
    |   |     |___... # 项目依赖库
    |   |
    |   |____ src/
    |   |     |___... # 项目源文件 / 加密源文件
    |   |
    |   |____ ex01_helloworld.exe # 项目可执行文件
    |   |____ ex01_helloworld.int # 入口文件
    |
    |___ ...
