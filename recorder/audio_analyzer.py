import threading
import logging
import time
import numpy as np
import librosa
import bisect
logger = logging.getLogger(__name__)

class AudioAnalyzer(threading.Thread):
    def __init__(self,
            sr,
            audio_data,
            default_bpm = 120,
            smooth_ratio = .2, 
            sample_time = 10, 
            recorder = None
            ):
        threading.Thread.__init__(self)
        self.data = []
        self.sr = sr
        self.sample_time = sample_time
        self.audio_data = audio_data
        self.output_beats = [0]
        self.output_period = 60/default_bpm
        self.smooth_ratio = smooth_ratio
        self.recorder = recorder
        self.mfcc_features = None
        self.ext_beat_times = None
        self.strength = None
        self.low_volume = 0 
        self.max_strength = 0
        self.last2 = time.time()
        self.update_prediction()
        self.__running = threading.Event()
        self.__running.set()

    def update_prediction(self):
        self.prediction = self.output_beats[-1] + self.output_period
        self.prediction_updated = True
        logger.info("Prediction updated...")
        logger.info("Period = %s"%self.output_period)
        if self.ext_beat_times is None:
            return
        extra_period = np.mean(self.ext_beat_times[1:] - self.ext_beat_times[:-1])
        extra_periods = [extra_period/i for i in range(4,0,-1)] + [extra_period] + [extra_period*i for i in range(1,5)]
        pos = bisect.bisect(extra_periods,self.output_period)
        if pos >= len(extra_periods):
            logger.critical("The Extra Periods is Too short!")
            logger.critical("%s"%extra_periods)
            return
        if self.output_period<0.30:
            self.output_period *= 2
        elif self.output_period>0.8:
            self.output_period /= 2
        if self.output_period<0.35 or (self.output_period<0.7 and self.output_period - extra_periods[pos-1] > extra_periods[pos]-self.output_period):
            extra_period = extra_periods[pos]
        else:
            extra_period = extra_periods[pos-1]
        new_period = self.output_period + (extra_period - self.output_period) * self.smooth_ratio
        new_prediction = self.output_beats[-1] + new_period
        if new_prediction > self.ext_beat_times[-1]:
            logger.info("The data is too short")
            return
        if new_prediction < self.ext_beat_times[0]:
            assert(False)
        logger.debug("Seems we can update prediction...")
        self.output_period = new_period
        pos = bisect.bisect(self.ext_beat_times,self.prediction)
        assert(self.ext_beat_times[pos-1] <= self.prediction and self.ext_beat_times[pos]>=self.prediction)
        if self.prediction-self.ext_beat_times[pos-1] > self.ext_beat_times[pos]-self.prediction:
            new_prediction = self.prediction + (self.ext_beat_times[pos] - self.prediction) * self.smooth_ratio
        else:
            new_prediction = self.prediction + (self.ext_beat_times[pos-1] - self.prediction) * self.smooth_ratio
        logger.debug("Change prediction from %s into %s"%(self.prediction,new_prediction))
        self.prediction = new_prediction

    def run(self):
        while self.__running.isSet():

            total_samples = len(self.audio_data)
            if total_samples < 512:
                time.sleep(.5)
                logger.info('No data found in cacher...')
                continue
            if total_samples > self.sr * self.sample_time:
                start_samples = total_samples - self.sr * self.sample_time
            else:
                start_samples = 0

            tmp_data = np.array(self.audio_data[start_samples:]).copy().astype(np.float32)
            start_time = start_samples / self.sr
            tempo, _beat_frames = librosa.beat.beat_track(y=tmp_data, sr=self.sr)
            beat_frames = _beat_frames + int(start_samples/512)
            beat_times = librosa.frames_to_time(beat_frames)
            mfcc = librosa.feature.mfcc(y=tmp_data, sr=self.sr, n_mfcc=13)
            beat_mfcc = librosa.util.sync(mfcc, _beat_frames)
            strength = librosa.feature.rmse(y = tmp_data)
            if len(beat_times) < 5:
                logger.debug("The beats count is not enough <%s>"%len(beat_times))
                continue

            self.strength = list(sorted(strength[0][-5:].tolist()))[3]
            self.max_strength = max(self.max_strength,self.strength)
            self.mfcc_features = np.mean(beat_mfcc[:,-5:],axis=1)

            k,b = np.polyfit(range(len(beat_times)),beat_times,1)
            self.ext_beat_times = k*np.linspace(0,len(beat_times)-1+180,len(beat_times)+180) + b
            self.max_strength *= 0.999
            current_tick = time.time()
            if current_tick - self.last2 > 1:
                self.last2 = current_tick
                self.status_all()
                if self.strength is not None and self.max_strength * 0.1 > self.strength:
                    self.low_volume += 1
                    logger.info("LOW VOLUME ! <%d>"%self.low_volume)
                else:
                    self.low_volume = 0
            time.sleep(0.01)

    def status_all(self):
        logger.debug("Strength = %d"%self.strength)
        logger.debug("Strength (MAX) = %d"%self.max_strength)
        logger.debug("Low Volume = %d"%self.low_volume)
        logger.debug("Running : %s"%self.__running)

    def stop(self):
        logger.warn("Stop signal received")
        self.__running.clear() 
