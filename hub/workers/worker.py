from threading import Thread

from jsonpickle import json

from hub.kinesis.data_kinesis import DataKinesis
from hub.kinesis.listener import Listener


class Worker(object):
    def __init__(self, stream_name: str, task_list, tries=None, num_workers=1):
        self.num_workers = num_workers
        self.stream_name = stream_name
        self.task_list = task_list
        self.tries = tries
        self.threads = []

    def process_records(self, record_kinesis):
        try:
            data: DataKinesis = json.loads(record_kinesis.get("Data").decode())
            name_task = data.get("task", "")
            task = self.task_list.get(name_task, None)
            # Not found task
            if task is None:
                raise NotImplementedError
            return task(data)
        except Exception:
            return None

    def start(self):
        for i in range(self.num_workers):
            listener = Listener(
                self.stream_name, self.process_records, self.tries
            )
            task = listener.run
            t = Thread(target=task)
            t.setDaemon(True)
            t.start()
            self.threads.append(t)
        return self.threads
