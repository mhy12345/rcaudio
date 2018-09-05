# rcaudio : A Realtime Audio Recording & Analyzing Library

## Introduction 

**rcaudio** Rcaudio is a real-time audio analysis library that allows you to simply record audio through a microphone and analyze.

It supports real-time analysis of :

* The raw audio data
* Volume
* Beat Information

For chinese documentation : [中文文档](http://mhy12345.xyz/technology/rcaudio-documentation/)
## Installation

```bash
pip install rcaudio
```

## Usage

### CoreRecorder

`CoreRecorder` is used to fetch raw data. When started, the audio data will be stored in the `CoreRecorder.buffer`.

```python
from rcaudio import CoreRecorder
CR = CoreRecorder(
        time = 10, #How much time to record
        sr = 1000 #sample rate
        )
CR.start()
while True:
    if not CR.buffer.empty():
        x = CR.buffer.get()
        print('*'*int(abs(x)))
```

### SimpleRecorder

In most cases, we use `SimpleRecorder`.  For efficiency consideration, the `SimpleRecorder`  should only be instantiated once. 

This class can register several `Analyzer`. 

When the function `start()` called, It will begin to record through microphone, and refresh the status of all the `Analyzer`

### Analyzers

All class extended from `BaseAnalyzer` can be registered into `SimpleRecorder`. For example `VolumeAnalyzer` can get the current volume of the microphone.


```python
import time
from rcaudio import SimpleRecorder,VolumeAnalyzer

SR = SimpleRecorder()
VA = VolumeAnalyzer(rec_time = 1)
SR.register(VA)
SR.start()
while True:
    print("VOLUME : ",VA.get_volume())
    time.sleep(1)
```

And beat analyzer can predict the beats from the music. (However, there will be some delay.)

```python
SR = SimpleRecorder(sr = 20000)
BA = BeatAnalyzer(rec_time = 15, initial_bpm = 120, smooth_ratio = .8)
SR.register(BA)
SR.start()
while True:
    print(BA.block_until_next_beat())
```

A FeatureAnalyzer can use to generate all user defined acoustic features. Just override the `data_process` function. (Current function are the calculation of the *Zero Crossing Rate*.

```python
SR = SimpleRecorder(sr = 1000)
FA = FeatureAnalyzer(refresh_time = 1)
SR.register(FA)
SR.start()
cpos = 0
while True:
	if len(FA.result) > cpos:
		print(FA.result[cpos])
		cpos += 1
	time.sleep(.01)
```

## Some note

Most function has the time delay about 1-2 seconds. I did lot effort to let the BeatAnalyzer looked as it is real-time. However, for the `FeatureAnalyzer`, if the feature extraction function are too slow compare to the microphone recording, the dalay may become huge. Decrease the sample rates would be a solution, but better solution would be DIY a analyzer yourself.
