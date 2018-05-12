import time

class BaseBeater:
    def __init__(self):
        self.STOP_SIGNAL_LENGTH = 15
        pass

    def next(self):
        pass

    def about_to_stop(self):
        pass

    def stop(self):
        pass

    def start(self):
        self.start_time = time.time()

    def get_start_time(self):
        return self.start_time
