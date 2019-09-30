from threading import Thread

from hub.kinesis.listener import Listener


class Worker(object):

    def __init__(self, stream_name: str, process_records,
                 tries=None, num_workers=1):
        self.num_workers = num_workers
        self.stream_name = stream_name
        self.process_records = process_records
        self.tries = tries
        self.threads = []

    def start(self):
        for i in range(self.num_workers):
            listener = Listener(
                self.stream_name, self.process_records, self.tries)
            task = listener.run
            t = Thread(target=task)
            t.setDaemon(True)
            t.start()
            self.threads.append(t)
        return self.threads
