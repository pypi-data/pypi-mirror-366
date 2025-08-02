# load gz lib
import xlrd


def function_core_a():
    print("Called from function_core_a, in folder")
    print(f"loaded orderedset, version: {xlrd.__version__}")
