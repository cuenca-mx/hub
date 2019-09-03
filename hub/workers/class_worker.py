from threading import Thread


class Worker(object):

    def __init__(self, task, num_workers=1):
        self.num_workers = num_workers
        self.task = task

    def start(self):
        for i in range(self.num_workers):
            t = Thread(target=self.task)
            t.daemon = True
            t.start()
