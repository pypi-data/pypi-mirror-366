import pygame
import tomli
import typer


def main():
    print("Test for poetry project!")
    print("Pygame version:", pygame.__version__)
    print("Tomli version:", tomli.__version__)
    print("Typer version:", typer.__version__)


if __name__ == "__main__":
    main()
