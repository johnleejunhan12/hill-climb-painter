try:
    from .read_write_parameter_json import *
except ImportError:
    from read_write_parameter_json import *


def foo():
    print(f"My __name__ is: {__name__}")
    param_dict = read_parameter_json()
    print(f"Parameters: {param_dict}")
    print(type(param_dict))



if __name__ == "__main__":
    foo()  # Call the function to test reading parameters