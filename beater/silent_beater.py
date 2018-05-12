from beater.base_beater import BaseBeater
import logging
import time
logger = logging.getLogger(__name__)

class SilentBeater(BaseBeater):
    def __init__(self,beats_info,mfccs_info):
        BaseBeater.__init__(self)
        self.beats_info = beats_info
        self.mfccs_info = mfccs_info
        self.pos = 0
        self.total_beats = min(len(mfccs_info),len(beats_info))

    def start(self):
        self.start_time = time.time()
        pass

    def next(self):
        self.pos += 1
        if self.pos >= self.total_beats:
            raise StopIteration("SilentBeater")
        return self.beats_info[self.pos-1], self.beats_info[self.pos] - self.beats_info[self.pos-1], self.mfccs_info[self.pos-1]

    def about_to_stop(self,addition_beats):
        if self.total_beats is None:
            return self.watcher.low_volume()
        else:
            time_left = self.total_beats - self.pos
            time_needed = addition_beats
            logger.info("CHECK STOP :%s %s %s"%(time_left,time_needed,time_needed >= time_left - 4))
            return time_needed >= time_left - 4
