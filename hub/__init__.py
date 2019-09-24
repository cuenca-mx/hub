from importlib import import_module
import types
import click
from jsonpickle import json

from hub.kinesis.data_kinesis import DataKinesis
from hub.workers import Worker


def init_workers(module, num_workers):
    """
    Find all function in the module that implement "kinesis_task" decorator.
    Group functions by "stream" param in decorator

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
                dict_functions = streams.get(kinesis_stream, dict())
                dict_functions[name] = obj_module
                streams[kinesis_stream] = dict_functions

    """
    A daemon is started for each "KinesisStream"
    and a group of functions is associated with a task selector
    """
    for stream, functions in streams.items():
        selector = task_selector(functions)
        w = Worker(stream, selector, None, num_workers)
        w.start()
    # Maintain live daemons
    while True:
        pass


def task_selector(tasks):
    def exec_task(record):
        print('\n\nRecord: ', record)
        request: DataKinesis = json.loads(record.get("Data").decode())
        name_task = request.get("task", "")
        task = tasks.get(name_task, None)
        if task is None:
            print("La tarea solicitada no existe: ", name_task)
            return None
        return task(request)

    return exec_task


@click.command()
@click.option("--app", help="Module to search Kinesis Tasks", required=True)
@click.option("--num_workers", default=1, help="Number of workers")
def cli_hub(app, num_workers):
    """
    Command Line Interface to Start Workers
    """
    print("Module Selected for Kinesis App: ", app)
    print("Workers: ", num_workers)
    try:
        module = import_module(app)
        init_workers(module, num_workers)
    except ModuleNotFoundError:
        print("Exited: Module Not Found Error")
