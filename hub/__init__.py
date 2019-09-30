import types
from jsonpickle import json

from hub.kinesis.data_kinesis import DataKinesis
from hub.workers import Worker


def init_workers(module, num_workers):
    """
    Init N workers for each "KinesisStream"
    Assign a group of functions
    """
    streams = find_decorated_functions(module)
    for stream, functions in streams.items():
        selector = task_selector(functions)
        w = Worker(stream, selector, None, num_workers)
        w.start()
    # Maintain live daemons
    while True:
        pass


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


def task_selector(tasks):
    """
       Wrapped Function to select the function to execute for new Records
       "Data.task" indicates the name of the function
    """
    def exec_task(record):
        request: DataKinesis = json.loads(record.get("Data").decode())
        name_task = request.get("task", "")
        task = tasks.get(name_task, None)
        if task is None:
            return None
        return task(request)
    return exec_task
