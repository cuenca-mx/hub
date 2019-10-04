import types

from .worker import Worker


def init_workers(module, num_workers):
    """
    Init N workers for each "KinesisStream"
    Assign a group of functions
    """
    streams = find_decorated_functions(module)
    workers_created = []
    for stream, task_list in streams.items():
        w = Worker(stream, task_list, None, num_workers)
        w.start()
        workers_created.append(w)
    return workers_created


def find_decorated_functions(module):
    """
    Find all function in the module that implement "kinesis_task" decorator.
    Group functions by "stream" param

    streams: (
        "stream1": (
            "task_A": <function task_A> ,
            "task_B": <function task_B>
        ) ,
        "stream2": (
            "task_X": <function task_X>
        )
    )
    """
    streams = dict()
    for name in dir(module):
        obj_module = getattr(module, name)
        if isinstance(obj_module, types.FunctionType):
            kinesis_stream = getattr(obj_module, "kinesis_task", None)
            if kinesis_stream is not None:
                print('Function', name, "() -->", kinesis_stream)
                group_functions = streams.get(kinesis_stream, dict())
                group_functions[name] = obj_module
                streams[kinesis_stream] = group_functions
    return streams
