import time
import queue
from .base_analyzer import BaseAnalyzer

class VolumeAnalyzer(BaseAnalyzer):
    def __init__(self,
            rec_time = 1
            ):
        BaseAnalyzer.__init__(self)
        self.pool = queue.Queue()
        self.cpos = 0
        self.rec_time = rec_time
        self.rec_size = None
        self.sum = 0
        self.total = 0

    def register_recorder(self,recorder):
        BaseAnalyzer.register_recorder(self,recorder)
        self.rec_size = self.sr * self.rec_time

    def run(self):
        while self.recorder.start_time is None:
            time.sleep(1)
        while self.running.isSet():
            while len(self.audio_data) > self.cpos:
                v = abs(self.audio_data[self.cpos])
                self.pool.put(v)
                self.total += 1
                self.sum += v
                self.cpos += 1
                if self.pool.qsize() >= self.rec_size:
                    v = self.pool.get()
                    self.total -= 1
                    self.sum -= v
            time.sleep(.1)

    def get_volume(self):
        if self.total == 0:
            return 0
        return self.sum / self.total
