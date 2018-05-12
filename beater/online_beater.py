from beater import BaseBeater
from recorder import RecorderWatcher
import numpy as np
import logging
import time
import threading
import bisect

class OnlineBeater(BaseBeater):
    def __init__(self):
        BaseBeater.__init__(self)
        self.watcher = RecorderWatcher()
        self.logger = logging.getLogger(__name__+".OnlineBeater")

    def start(self):
        self.watcher.start()

    def next(self):
        return self.watcher.get_prediction_and_update(),self.watcher.get_period(),self.watcher.get_mfcc_features()

    def about_to_stop(self,addition_beats):
        return self.watcher.low_volume()

    def stop(self):
        self.logger.critical("STOP SIGNAL OCCURE")
        self.watcher.stop()

    def get_start_time(self):
        return self.watcher.start_time

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    instance = BeaterWatcher()
    instance.start()


