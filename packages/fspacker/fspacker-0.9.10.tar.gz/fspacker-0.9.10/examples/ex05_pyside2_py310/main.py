import platform

import PySide2


def main():
    print("Hello from ex05-pyside2-py311!")
    print(f"Current python ver: {platform.python_version()}")
    print(f"Pyside2 version: {PySide2.__version__}")


if __name__ == "__main__":
    main()
