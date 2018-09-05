import threading
import logging
from pyaudio import PyAudio,paInt16
import numpy as np
import queue
import time

class CoreRecorder(threading.Thread):
    def __init__(self,
            time = None, #How much time to the end
            sr = 20000, #Sample rate
            batch_num  = 600, #Batch size (how much data for a single fetch)
            frames_per_buffer = 600 
            ):
        threading.Thread.__init__(self)
        self.time = time
        self.sr = sr
        self.batch_num = batch_num
        self.data_alter = threading.Lock()
        self.frames_per_buffer = frames_per_buffer
        self.logger = logging.getLogger(__name__ + '.CoreRecorder')
        self.buffer = queue.Queue()
        self.start_time = None
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        self.logger.debug("Start to recording...")
        self.logger.debug("  Time = %s"%self.time)
        self.logger.debug("  Sample Rate = %s"%self.sr)
        self.start_time = time.time()
        pa=PyAudio()
        stream=pa.open(format = paInt16,channels=1, rate=self.sr,input=True, frames_per_buffer=self.frames_per_buffer)
        my_buf=[]
        count=0
        if self.time is None:
            total_count = 1e10
        else:
            total_count = self.time * self.sr / self.batch_num
        while count< total_count and self.__running.isSet():
            datawav = stream.read(self.batch_num, exception_on_overflow = True)
            datause = np.fromstring(datawav,dtype = np.short)
            for w in datause:
                self.buffer.put(w)
            count+=1
        stream.close()

    def save_wave_file(self,filename,data):
        wf=wave.open(filename,'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(self.sr)
        wf.writeframes(b"".join(data))
        wf.close()

    def stop(self):
        self.__running.clear()
