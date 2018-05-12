from beater.base_beater import BaseBeater
from recorder import RecorderWatcher
import logging
logger = logging.getLogger(__name__)

class BPMPresetBeater(BaseBeater):
    def __init__(self,bpm,offset = 0,total_beats = None):
        BaseBeater.__init__(self)
        self.watcher = RecorderWatcher()
        self.bpm = bpm
        self.offset = offset
        self.pos = offset
        self.secs_per_beats = 1/bpm*60
        self.total_beats = total_beats
        self.count = 0

    def start(self):
        self.watcher.start()

    def next(self):
        self.count += 1
        ret = self.pos
        self.pos += self.secs_per_beats
        if not self.total_beats is None and self.count >= self.total_beats:
            raise StopIteration("BPMPresetBeater")
        return ret,self.secs_per_beats,self.watcher.get_mfcc_features()

    def about_to_stop(self,addition_beats):
        if self.total_beats is None:
            return self.watcher.low_volume()
        else:
            time_left = self.total_beats - self.count
            time_needed = addition_beats
            logger.info("CHECK STOP :%s %s %s"%(time_left,time_needed,time_needed >= time_left - 4))
            return time_needed >= time_left - 4

    def get_start_time(self):
        return self.watcher.start_time

    def stop(self):
        logger.critical("STOP SIGNAL OCCURE")
        self.watcher.stop()
