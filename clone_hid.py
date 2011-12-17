#!/usr/bin/python

import sys
from hid import HIDProxWriter
import q5

hid = HIDProxWriter(sys.argv[1])
payload = hid.encode()

o = q5.Programmer()
o.reset()
o.data(payload)
o.configure(o.HIDPROX)
o.dump()
