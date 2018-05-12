from beater import OnlineBeater,BPMPresetBeater
import logging
import time
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

DC = OnlineBeater()
DC.start()
while True:
    start,dur,fea = DC.next()
    while True:
        if DC.watcher.start_time is not None and time.time() - DC.watcher.start_time > start:
            break
        time.sleep(.01)
    print("ITER")
