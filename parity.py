
def odd(bitstream):
    count = 0
    for i in bitstream:
        if i == '1':
            count += 1

    return '1' if count%2 == 0 else '0'

def even(bitstream):
    count = 0
    for i in bitstream:
        if i == '1':
            count += 1

    return '1' if count%2 == 1 else '0'
