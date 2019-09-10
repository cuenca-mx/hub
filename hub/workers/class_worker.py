from threading import Thread

from hub.kinesis.listener import Listener


class Worker(object):

    def __init__(self, num_workers=1):
        self.num_workers = num_workers

    def start(self):
        for i in range(self.num_workers):
            listener = Listener()
            task = listener.run()
            t = Thread(target=task)
            t.daemon = True
            t.start()
