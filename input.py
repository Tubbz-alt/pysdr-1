import numpy as np
import time
import sys

import ext

class SigInput:
    def __init__(self):
        self.sample_rate = 0
        self.no_channels = 0

    def read(self, frames):
        raise NotImplementedError("read() method must be overrided")

    def start(self):
        raise NotImplementedError("start() method must be overrided")

class RawSigInput(SigInput):
    def __init__(self, sample_rate, no_channels, dtype, file):
        self.sample_rate = sample_rate
        self.no_channels = no_channels
        self.dtype = dtype
        self.file = file

    def read(self, frames):
        read_len = frames * self.dtype.itemsize * self.no_channels
        string = ""

        while len(string) < read_len:
            string += self.file.read(read_len - len(string))

        if self.no_channels == 1:
            return np.fromstring(string, dtype=self.dtype).astype(np.float32)
        elif self.no_channels == 2 and self.dtype == np.dtype(np.float32):
            return np.fromstring(string, dtype=np.complex64)
        else:
            raise NotImplementedError("unimplemented no of channels and type combination")

    def start(self):
        pass

class JackInput(SigInput):
    def __init__(self, name):
        self.name = name
        self.handle = ext.jack_init(name)
        self.sample_rate = ext.jack_get_sample_rate(self.handle)

    def read(self, frames):
        while True:
            r = ext.jack_gather_samples(self.handle, frames)

            if r != None:
                return r

            time.sleep(float(frames) / self.sample_rate / 10)

    def start(self):
        ext.jack_activate(self.handle)
