
class Programmer():
    HIDPROX = 0

    def __init__(self):
        self.commands = []

    def reset(self):
        self.commands.append("w00E601f004")

    def data(self, bytestream):
        registers_4B = ["".join(bytestream[i:i+4]) for i in range(len(bytestream)) if i%4 == 0]
        for i,data in enumerate(registers_4B):
            self.commands.append("w%02d%s" % (i+1, data))

    def configure(self, cardtype):
        if cardtype == self.HIDPROX:
            self.commands.append("w0060018056")
        else:
            raise "Unknown card"

    def dump(self):
        print "Enter the following commands on your AGC reader:"
        for i in self.commands:
            print i
