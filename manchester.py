
def verify(bitstream):
    i = 0
    while i < len(bitstream):
        assert bitstream[i] != bitstream[i+1]
        i += 2

def decode(bitstream):
    return "".join([bitstream[i] for i in range(len(bitstream)) if i % 2 == 0])

def encode(bitstream):
    encoded_buf = []
    opposite = lambda x: '1' if int(x) == 0 else '0'
    [encoded_buf.extend(bitstream[i]) or encoded_buf.extend(opposite(bitstream[i])) for i in range(len(bitstream))]
    return "".join(encoded_buf)

