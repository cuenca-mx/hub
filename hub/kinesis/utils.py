from functools import wraps

from hub.kinesis.listener import Listener


def kinesis(stream_name):
    def decorator(function):
        def wrapped(*args, **kwargs):
            consumer = Listener(stream_name, function, 2)
            consumer.run()
        return wrapped
    return decorator
