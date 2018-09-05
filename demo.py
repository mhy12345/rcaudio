from rcaudio import *
import time
import logging


logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')


def demo1():
    CR = CoreRecorder(
            time = 10, 
            sr = 1000,
            batch_num = 100,
            frames_per_buffer = 100,
            )
    CR.start()
    while True:
        if not CR.buffer.empty():
            x = CR.buffer.get()
            print('*'*int(abs(x)))

def demo2():
    SR = SimpleRecorder()
    VA = VolumeAnalyzer(rec_time = 1)
    SR.register(VA)
    SR.start()
    while True:
        print("VOLUME : ",VA.get_volume())
        time.sleep(1)


def demo3():
    SR = SimpleRecorder(sr = 20000)
    BA = BeatAnalyzer(rec_time = 15, initial_bpm = 120, smooth_ratio = .8)
    SR.register(BA)
    SR.start()
    while True:
        print(BA.block_until_next_beat())

demo3()
