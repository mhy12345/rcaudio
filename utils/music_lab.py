import librosa
import logging
import numpy as np
logger = logging.getLogger(__name__)

def music_analyze(music_path,
        start_time = None,
        duration = None,
        sr = 20000,
        ):
    _sr = sr
    if start_time is None:
        start_time = 0.0
    logger.info("Analyze music at <%s> (%s:%s)"%(music_path,start_time,start_time+duration if not duration is None else None))
    y, sr = librosa.load(music_path,offset=start_time,duration=duration,sr = _sr)
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    tempo, beat_frames = librosa.beat.beat_track(y=y_percussive,sr=sr)
    beat_time = librosa.frames_to_time(beat_frames)
    logger.info("%d beats found in the audio"%len(beat_time))
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    beat_mfcc = librosa.util.sync(mfcc, beat_frames)
    return beat_time,beat_mfcc
