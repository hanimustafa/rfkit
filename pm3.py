#!/usr/bin/python

import Gnuplot
      
class OutOfSamples(Exception):
    pass

class Pm3Reader:
    def __init__(self, filename):
        self.fd = open(filename, 'r')
        self.samples = []
        self.waves = []
        self.first = 0
        self.current = 0
        self.filename = filename
        self.plotter = Gnuplot.Gnuplot()

    def load(self):
        self.samples = self.fd.readlines()
        self.verify()
        self.sync()
        print "Loaded %d samples, sync at %d" % (len(self.samples), self.first)

    def verify(self):
        try:
            line = 0
            for i,sample in enumerate(self.samples):
                line = i + 1
                self.samples[i] = int(sample)
        except ValueError:
            print "Invalid Pm3 entry at line %d" % line
            raise

    def sync(self):
        '''Sync to first lo-hi transition'''
        self.first = self._next_lo_hi()
        self.current = self.first

    def analyse(self):
        last = self.current
        while True:
            try:
                self.current = self._next_lo_hi()
                self._store_wave(last, self.current)
                last = self.current
            except OutOfSamples:
                break

    def plot(self):
        data = Gnuplot.Data(range(0,len(self.samples)),
                            self.samples,
                            title='Raw Signal',
                            with_='line lc "orange"')
        self.plotter('set output "%s"' % (self.filename + ".png"))
        self.plotter('set terminal png size %d,480' % (len(self.samples)*2))
        self.plotter('set xtics 100 rotate')
        self.plotter('set ytics 20')
        self.plotter('set grid')
        self.plotter.plot(data)
 
    def __del__(self):
        self.fd.close()

    def _next_lo_hi(self):
        self.hipeak = self._next_hi_lo()
        noise_factor = 4
        for i,sample in enumerate(self.samples[self.hipeak:], start=self.hipeak):
            if self.samples[i-1] < sample and abs(sample - self.samples[i-1]) > noise_factor:
                return i
        raise OutOfSamples

    def _next_hi_lo(self):
        for i,sample in enumerate(self.samples[self.current:], start=self.current):
            if self.samples[i-1] > sample:
                return i
        raise OutOfSamples

    def _store_wave(self, start, end):
        wave = dict()
        wave['start'] = start
        wave['end'] = end
        wave['count'] = end - start
        if wave['count'] <= 8:
            wave['value'] = 0
        else:
            wave['value'] = 1
        self.waves.append(wave)


