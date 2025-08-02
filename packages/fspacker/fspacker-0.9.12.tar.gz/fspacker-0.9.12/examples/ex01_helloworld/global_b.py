import core
from core import core_c


def function_global_b():
    print("Called from function_global_b, single file")
    core.core_a.function_core_a()
    core_c.function_core_c()
