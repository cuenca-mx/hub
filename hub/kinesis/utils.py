def kinesis_task(stream: str):
    def decorator(function):
        def new_function(*args, **kwargs):
            return function(*args, **kwargs)
        setattr(new_function, "kinesis_task", stream)
        return new_function
    return decorator
