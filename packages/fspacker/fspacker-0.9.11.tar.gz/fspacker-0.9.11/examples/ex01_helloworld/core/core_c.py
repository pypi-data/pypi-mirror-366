from mathtools.algorithms import factorial


def function_core_c():
    print("Called from function_core_c, in folder")
    for i in range(10):
        print(f"{factorial(i)=}")
