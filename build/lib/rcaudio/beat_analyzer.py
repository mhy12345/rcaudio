import threading
import logging
import time
import numpy as np
import librosa
import bisect
import math
from .base_analyzer import BaseAnalyzer

class BeatAnalyzer(BaseAnalyzer):
    def __init__(self,
            rec_time = 5,
            initial_bpm = 120,
            smooth_ratio = .2
            ):
        BaseAnalyzer.__init__(self)
        self.initial_k = 60 / initial_bpm
        self.current_b = time.time()
        self.current_k = self.initial_k
        self.expected_b = None
        self.expected_k = None
        self.beat_count = 0
        self.rec_time = rec_time
        self.smooth_ratio = smooth_ratio

    def register_recorder(self,recorder):
        BaseAnalyzer.register_recorder(self,recorder)
        self.rec_size = self.sr * self.rec_time

    def run(self):
        while self.recorder.start_time is None:
            time.sleep(1)
        self.current_b = time.time()
        self.start_time = self.recorder.start_time
        while self.running.isSet():
            if len(self.audio_data) < 4 * self.sr:
                time.sleep(.5)
                self.logger.debug("The data is not enough...")
                continue
            start_samples = len(self.audio_data) - self.rec_size if len(self.audio_data) > self.rec_size else 0
            data = np.array(self.audio_data[start_samples:]).astype(np.float32)
            start_time = start_samples / self.sr
            tmpo, _beat_frames = librosa.beat.beat_track(y=data,sr = self.sr)
            beat_times = librosa.frames_to_time(_beat_frames) + start_time + self.start_time

            if len(beat_times) < 5:
                self.logger.debug("The beats count <%d> is not enough..."%len(beat_times))
                continue
            
            self.expected_k,self.expected_b = np.polyfit(range(len(beat_times)),beat_times,1)

    def block_until_next_beat(self):
        if self.expected_b is None:
            now = time.time()
            pred_i = math.ceil((now - self.current_b)/self.current_k)
            self.beat_count += pred_i
            pred_v2 = pred_i * self.current_k + self.current_b
            pred_v1 = pred_v2 - self.current_k
            pred = pred_v2
        else:
            now = time.time()
            pred_i = math.ceil((now - self.current_b)/self.current_k)
            pred_v2 = pred_i * self.current_k + self.current_b
            pred_v1 = pred_v2 - self.current_k

            exp_i = math.ceil((pred_v2 - self.expected_b)/self.expected_k)
            exp_v2 = exp_i * self.expected_k + self.expected_b
            exp_v1 = exp_v2 - self.expected_k
            if (pred_v2-exp_v1) < (exp_v2-pred_v2):
                pred = pred_v2 + (exp_v1-pred_v2)*(1-self.smooth_ratio)
                self.beat_count += pred_i 
            else:
                pred = pred_v2 + (exp_v2-pred_v2)*(1-self.smooth_ratio)
                self.beat_count += pred_i
        self.current_b = pred
        self.current_k = pred - pred_v1
        if not self.expected_k is None:
            self.current_k = self.current_k + (self.expected_k - self.current_k)*(1-self.smooth_ratio)
        if self.current_k < self.initial_k*.45:
            self.current_k *= 2
        if self.current_k > self.initial_k * 2.1:
            self.current_k /= 2
        while time.time() < pred:
            time.sleep(.01)
        return self.beat_count

