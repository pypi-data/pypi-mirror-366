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
