from core.core_a import function_core_a
from core.core_b import function_core_b

from modules.mod_a import function_mod_a


def function_mod_b():
    print("Called from function_mod_b, in folder")
    function_mod_a()
    function_core_a()
    function_core_b()
