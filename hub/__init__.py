from hub.workers import Worker
from importlib import import_module
import types


def init_workers(module):
    """
    Find all function in the module that implement "kinesis_task" decorator.
    Init a daemon to listen and respond in "Kinesis Data Streams"
    """
    for name in dir(module):
        obj_module = getattr(module, name)
        if isinstance(obj_module, types.FunctionType):
            kinesis_stream = getattr(obj_module, "kinesis_task", None)
            if kinesis_stream is not None:
                print(name + ": " + kinesis_stream)
                w = Worker(kinesis_stream, obj_module)
                w.start()


def init_service(includes: list):
    for include in includes:
        module = import_module(include)
        init_workers(module)
