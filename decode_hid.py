#!/usr/bin/python

import sys
from hid import HIDProxReader

pm3 = HIDProxReader(sys.argv[1])
pm3.load()
pm3.analyse()
pm3.plot()
