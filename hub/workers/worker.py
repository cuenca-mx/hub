from threading import Thread
from typing import Callable, Dict

from hub.kinesis.listener import Listener


class Worker(object):
    def __init__(
        self,
        stream_name: str,
        task_list: Dict[str, Callable],
        tries: int = None,
        num_workers: int = 1,
    ):
        self.num_workers = num_workers
        self.stream_name = stream_name
        self.task_list = task_list
        self.tries = tries
        self.threads = []

    def process_records(self, data: Dict):
        name_task = data.get("task", "")
        task = self.task_list.get(name_task, None)
        # Not found task
        if task is None:
            raise NotImplementedError
        return task(data)

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
