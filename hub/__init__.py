from hub.workers import Worker
from importlib import import_module
import types
import click


def init_workers(module, num_workers):
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
                w = Worker(kinesis_stream, obj_module, num_workers)
                w.start()


def init_service(include: list):
    for i in include:
        module = import_module(i)
        init_workers(module)


@click.command()
@click.option("--module", help="Module to search Kinesis Tasks", required=True)
@click.option("--workers", default=1, help="Number of workers")
def cli_hub(app, num_workers):
    """
    Command Line Interface to Start Workers
    """
    print("Module Selected for Kinesis App: "+app)
    try:
        module = import_module(app)
        init_workers(module, num_workers)
    except ModuleNotFoundError:
        print("Exited: Module Not Found Error")
