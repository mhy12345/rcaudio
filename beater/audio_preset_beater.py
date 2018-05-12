from beater.base_beater import BaseBeater
from utils.music_lab import music_analyze

class AudioPresetBeater(BaseBeater):
    def __init__(self,music_path):
        BaseBeater.__init__(self)
        self.beat_time,self.beat_mfcc = music_analyze(music_path)
        self.pos = 0

    def next(self):
        self.pos += 1
        if self.pos >= len(self.beat_time):
            raise StopIteration("AudioPresetBeater")
        return self.beat_time[self.pos-1], self.beat_time[self.pos] - self.beat_time[self.pos-1], self.beat_mfcc[:,self.pos-1]

    def about_to_stop(self, beats_left):
        return len(self.beat_time) - self.pos <= beats_left
