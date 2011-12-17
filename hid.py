#!/usr/bin/python

from pm3 import Pm3Reader
import manchester
import parity

class HIDProxReader(Pm3Reader):
    max_consecutive_manchester_bits = 5

    def __init__(self, filename):
        self.bitstream = []
        self.sof = []
        Pm3Reader.__init__(self, filename)

    def analyse(self):
        Pm3Reader.analyse(self)
        self._generate_bitstream()
        self.sof = self._find_start_of_frames()
        self.cards = self._parse_start_of_frames()
        for card in self.cards:
            print self._card_info(card)

    def plot(self):
        if len(self.cards) > 0:
            self.plotter.title('Waveform for HID prox card %s' %  self._card_info(self.cards[0]))
        else:
            self.plotter.title('Waveform for unknown HID prox card')

        self.plotter('set style rectangle back fillcolor rgb "#FFA500" fs solid 0.20 noborder')
        laststream = {}
        for stream in self.bitstream:
            if laststream != stream and self._plot_stream(stream): 
                self._plot_stream(stream)
                laststream = stream
        for frame in self.sof:
            self._plot_sof(frame)

        Pm3Reader.plot(self)

    def _card_info(self, card):
            return "%s: (format %s) company %s, facility %s, card id %s (even=%d,odd=%d)" % \
                    (hex(int(card, base=2)),
                    hex((int(card, base=2) >> 26)&0x2ff),
                    hex(int(card, base=2) >> 37),
                    hex((int(card, base=2)>>17)&0xff),
                    hex((int(card, base=2)>>1) & 0xffff),
                    (int(card, base=2)&0x1),
                    (int(card, base=2)>>25) & 0x1)

    def _plot_stream(self, stream):
        if stream.has_key('first_wave') and stream['first_wave'] >= 0 and stream.has_key('last_wave') and stream['value'] == 1:
            self.plotter('set object rect from %d, graph 0 to %d, graph 1' % \
                            (self.waves[stream['first_wave']]['start'], self.waves[stream['last_wave']]['end']))
            return True
        else:
            return False
        
    def _plot_sof(self, frame):
        label = "Start of Frame"
        i = self.waves[self.bitstream[frame]['first_wave']]['start']
        self.plotter('set object %d rect at %d,%d size char %d, char 3' % (i, i, 0, len(label)+10))
        self.plotter('set object %d rect fc rgb "#C0C0C0" fs solid 0.90 border -1 front' % i)
        self.plotter('set label %d at %d,%d "%s" front center textcolor rgb "#FFFFFF" font "Arial,24"' % (i, i, 0, label))

    def _num_fc8_waves_to_bits(self, num):
        return (num+1)/6

    def _num_fc10_waves_to_bits(self, num):
        return (num+1)/5

    def _generate_bitstream(self):
        lastcount = 0
        first = {'first_wave': 0, 'value': self.waves[0]['value']}
        self.bitstream.append(first)
        for num,wave in enumerate(self.waves):
             if self.bitstream[-1]['value'] == wave['value']:
                lastcount += 1
             elif self.bitstream[-1]['value'] == 0:
                assert (self._num_fc8_waves_to_bits(lastcount) < HIDProxReader.max_consecutive_manchester_bits)
                self.bitstream[-1]['last_wave'] = num-1
                i = 1
                while i < self._num_fc8_waves_to_bits(lastcount):
                    self.bitstream.append(self.bitstream[-1])
                    i += 1
                lastcount = 1
                self.bitstream.append({'first_wave': num, 'value': 1})
             else:
                assert (self._num_fc10_waves_to_bits(lastcount) < HIDProxReader.max_consecutive_manchester_bits)
                self.bitstream[-1]['last_wave'] = num-1
                i = 1
                while i < self._num_fc10_waves_to_bits(lastcount):
                    self.bitstream.append(self.bitstream[-1])
                    i += 1
                self.bitstream.append({'first_wave': num, 'value': 0})
                lastcount = 1

    def _find_start_of_frames(self):
        frames = []
        i = 0
        while i < len(self.bitstream) - 48:
            if (self._is_sof(self.bitstream, i)):
                frames.append(i)
            i += 1
        return frames

    def _is_sof(self, bitstream, index):
        sof = [0,0,0,1,1,1]
        for i,bit in enumerate(sof):
            if sof[i] != bitstream[index+i]['value']:
                return False
        return True

    def _parse_start_of_frames(self):
        cards = []
        for i in self.sof:
            try:
                card_bitstream = self._get_hid_bitstream(i)
                manchester.verify(card_bitstream)
                cards.append(manchester.decode(card_bitstream))
            except:
                pass
        print "Found %d cards in total" % len(cards)
        return cards

    def _get_hid_bitstream(self, offset):
        sof_len = 8 #0x1d
        cardid_len = 48*2 # 48-bit card id, manchester encoded
        return [str(self.bitstream[i]['value']) for i in range(offset+sof_len, offset+cardid_len)]

class HIDProxWriter():
    def __init__(self, secret):
        self.secret = int(secret)

    def encode(self):
        preamble = '1d' # 0x1d
        company_id = '0000001'
        card_format = '01000000000'
        facility_code = bin(0x80 | (self.secret >> 16))[2:] 
        zeropad = lambda x: '0' if len(x)%2 == 1 else ''
        card_id = bin(self.secret&0xffff)[2:]
        card_id = zeropad(card_id) + card_id
        ep = parity.even(facility_code + card_id[:4])
        op = parity.odd(card_id[4:])

        # 44-bit format
        binary_stream = company_id + card_format + ep + facility_code + card_id + op
        encoded = manchester.encode(binary_stream)
        hex_encoded = [preamble] + [hex(int(encoded[i:i+8], base=2))[2:] for i in range(len(encoded)) if i % 8 == 0]
        return hex_encoded
