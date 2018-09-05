from .core_recorder import CoreRecorder
import threading
import logging
import time


class SimpleRecorder(threading.Thread):
    def __init__(self,
            sr = 2000, #Sample Rate
            ):
        threading.Thread.__init__(self)
        self.audio_data = []
        self.audio_lock = threading.Lock()
        self.logger = logging.getLogger(__name__+".SimpleWatcher")
        self.recorder = CoreRecorder(sr = sr)
        self.analyzers = []
        self.sr = sr
        self.start_time = None
        self.__running = threading.Event()
        self.__running.set()

    def register(self,analyzer):
        self.analyzers.append(analyzer)
        analyzer.register_recorder(self)

    def run(self):
        self.recorder.start()
        for analyzer in self.analyzers:
            analyzer.start()
        while self.__running.isSet():
            self.start_time = self.recorder.start_time
            if self.start_time is not None:
                break
            time.sleep(.05)

        while self.__running.isSet():
            while not self.recorder.buffer.empty():
                v = self.recorder.buffer.get()
                self.audio_data.append(v)

        for analyzer in self.analyzers:
            analyzer.stop()
            analyzer.join()
        self.recorder.stop()
        self.recorder.join()

    def stop(self):
        self.logger.warn("Stop Signal Received!")
        self.__running.clear()

