import types

from hub.workers.worker import Worker

import os

import boto3

ACCESS_KEY = os.environ['ACCESS_KEY']
SECRET_KEY = os.environ['SECRET_KEY']
REGION_NAME = os.environ['REGION_NAME']

kinesis_client = boto3.client(
    'kinesis',
    region_name=REGION_NAME,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

dynamo_client = boto3.client(
    'dynamodb',
    region_name=REGION_NAME,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)


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
