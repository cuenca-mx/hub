def kinesis():
    def decorator(function):
        def new_function(*args, **kwargs):
            print(f"Function {f.__name__}() called!")
            return function(*args, **kwargs)
        return new_function
    return decorator
