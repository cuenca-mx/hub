from hub.kinesis.listener import Listener


def kinesis(stream_name):
    def decorator(function):
        consumer = Listener(stream_name, function, 2)
        consumer.run()
    return decorator
