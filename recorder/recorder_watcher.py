from recorder import SimpleRecorder
from recorder import AudioAnalyzer
import logging
import numpy as np
import threading
import time
import bisect

class RecorderWatcher(threading.Thread):
    def __init__(self,
            defaut_bpm = 120,
            master = None
            ):
        threading.Thread.__init__(self)
        self.audio_data = []
        self.audio_lock = threading.Lock()
        self.beat_frames = []
        self.master = master
        self.logger = logging.getLogger(__name__+".BeaterWatcher")
        self.start_time = None
        self.silence_period = 2
        self.recorder = SimpleRecorder()
        self.analyzer = AudioAnalyzer(
                sr = self.recorder.sr,
                audio_data = self.audio_data,
                recorder = self.recorder
                )
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        self.recorder.start()
        self.analyzer.start()

        while True:
            self.start_time = self.recorder.start_time
            if self.start_time is not None:
                break
            time.sleep(0.01)

        self.last_ticks = 0
        while self.__running.isSet():
            current_tick = time.time() - self.start_time
            if self.get_prediction() < current_tick and self.get_prediction() < self.last_ticks:
                self.last_ticks = current_tick
                self.logger.info("Tick <outside>!")
            elif self.analyzer.output_beats[-1] < current_tick and self.analyzer.output_beats[-1] > self.last_ticks:
                self.last_ticks = current_tick
                self.logger.info("Tick <onside>!")
            elif self.analyzer.output_beats[-1] > current_tick:
                posA = bisect.bisect(self.analyzer.output_beats,current_tick)
                posB = bisect.bisect(self.analyzer.output_beats,self.last_ticks)
                if posA != posB:
                    self.logger.info("Tick <inside>!")
                    self.last_ticks = current_tick
            self.logger.debug("Audio data length : %d"%len(self.audio_data))
            if not self.recorder.isAlive():
                break
            if self.recorder.buffer.empty():
                time.sleep(.1)
                continue
            while not self.recorder.buffer.empty():
                v = self.recorder.buffer.get()
                self.analyzer.audio_data.append(v)
            wavdata = self.analyzer.audio_data
            wavtime = np.arange(0,len(wavdata))
            time.sleep(.05)
        self.analyzer.stop()
        self.analyzer.join()
        self.recorder.stop()
        self.recorder.join()

    def get_prediction(self):
        return self.analyzer.prediction

    def get_prediction_and_update(self):
        self.logger.info("Pull.")
        old_prediction = self.analyzer.prediction
        self.analyzer.output_beats.append(old_prediction)
        self.analyzer.update_prediction()
        return old_prediction

    def get_period(self):
        return self.analyzer.output_period

    def get_mfcc_features(self):
        return self.analyzer.mfcc_features

    def low_volume(self):
        return self.analyzer.low_volume > self.silence_period

    def stop(self):
        self.logger.warn("Stop signal received")
        self.__running.clear() 
