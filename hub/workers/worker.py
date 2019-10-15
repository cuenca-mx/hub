from threading import Thread
from typing import Callable, Dict

from hub.db.dynamo import write_to_db
from hub.kinesis.data_kinesis import DataKinesis
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
        try:
            name_task = data.get('task', '')
            uuid = data.get("uuid")
            if uuid is None:
                raise ValueError
            unique_trans = write_to_db(uuid)
            if unique_trans:
                task = self.task_list.get(name_task, None)
                # Not found task
                if task is None:
                    raise NotImplementedError
                body = task(data.get('body'))
                res = DataKinesis(
                    uuid=data.get("uuid"),
                    task=data.get("task"),
                    body=body,
                    headers=dict(),
                )
                return res.to_dict()
        except ValueError:
            return DataKinesis(
                uuid="",
                task="",
                body=dict(error="UUID not assigned"),
                headers=dict(),
            ).to_dict()
        except NotImplementedError:
            return DataKinesis(
                uuid=data.get("uuid"),
                task="",
                body=dict(error="Task not implemented"),
                headers=dict(),
            ).to_dict()
        except Exception as ex:
            return DataKinesis(
                uuid=data.get("uuid"),
                task="",
                body=dict(error=repr(ex)),
                headers=dict(),
            ).to_dict()

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
