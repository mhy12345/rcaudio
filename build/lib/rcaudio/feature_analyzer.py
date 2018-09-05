from .base_analyzer import BaseAnalyzer
import librosa
import time
import math
import numpy as np

class FeatureAnalyzer(BaseAnalyzer):
    def __init__(self,
            refresh_time = 1
            ):
        BaseAnalyzer.__init__(self)
        self.refresh_time = refresh_time
        self.cpos = 0
        self.result = []

    def register_recorder(self,recorder):
        BaseAnalyzer.register_recorder(self,recorder)
        self.refresh_size = self.sr * self.refresh_time

    def data_process(self,data):
        def ZeroCR(waveData,frameSize,overLap):
            #http://ibillxia.github.io/blog/2013/05/15/audio-signal-processing-time-domain-ZeroCR-python-realization/
            wlen = len(waveData)
            step = frameSize - overLap
            frameNum = math.ceil(wlen/step)
            zcr = np.zeros((frameNum,1))
            for i in range(frameNum):
                curFrame = waveData[np.arange(i*step,min(i*step+frameSize,wlen))]
                curFrame = curFrame - np.mean(curFrame) # zero-justified
                zcr[i] = sum(curFrame[0:-1]*curFrame[1::]<=0)
            return zcr
        zcr = ZeroCR(data,512,0)
        return data[0]

    def run(self):
        while self.recorder.start_time is None:
            time.sleep(1)

        while self.running.isSet():
            while len(self.audio_data) > self.cpos + self.refresh_size:
                data = np.array(self.audio_data[self.cpos:self.cpos + self.refresh_size]).astype(np.float32)
                data = self.data_process(data)
                self.result.append(data)
                self.cpos += self.refresh_size

