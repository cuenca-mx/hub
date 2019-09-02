from threading import Thread


class Worker(object):

    def __init__(self, num_workers=1):
        self.num_workers = num_workers

    def start_worker(self, task, args):
        args = args or ()
        for i in range(self.num_workers):
            t = Thread(target=task, args=args)
            t.daemon = True
            t.start()
