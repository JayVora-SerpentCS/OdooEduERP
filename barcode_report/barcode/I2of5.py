# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""barcode.i2of5"""

from barcode.base import Barcode
from barcode.errors import *


LEFT = '1010'
RIGHT = '11101'

# Narrow & Wide components
CODES = {
         '0': 'NNWWN',   '1': 'WNNNW',
         '2': 'NWNNW',   '3': 'WWNNN',
         '4': 'NNWNW',   '5': 'WNWNN',
         '6': 'NWWNN',   '7': 'NNNWW',
         '8': 'WNNWN',   '9': 'NWNWN'
        }


class Interleaved2of5(Barcode):
    """Initializes I2OF5 object.
    :parameters:
        i2of5 : String
            The i2of5 number as string.
        writer : barcode.writer Instance
            The writer to render the barcode (default: SVGWriter).
    """
    name = 'I2OF5'

    def __init__(self, i2of5, writer=None):
        if not i2of5.isdigit():
            raise ValueError('Code can only contain numbers.')
        if not len(i2of5) % 2 == 0:
            raise ValueError('Code must have an even number of digits')
        self.i2of5 = i2of5
        self.writer = writer or Barcode.default_writer()

    def __unicode__(self):
        return self.i2of5

    def get_fullcode(self):
        return self.i2of5

    def build(self):
        """Builds the barCode pattern from 'self.i2of5'
        :returns: The pattern as string
        :return type: String
        """
        code = LEFT[:]
        for (i, j) in zip(self.i2of5[0::2], self.i2of5[1::2]):
            for (k, l) in zip(CODES[i], CODES[j]):
                code += k + l
        code += RIGHT

        pattern = []
        for i, c in enumerate(code):
            if i % 2 == 0:  # bar
                c = c.replace('N', '1').replace('W', '11')
            else:      # space
                c = c.replace('N', '0').replace('W', '00')
            pattern.append(c)

        code = ''.join(pattern)
        return [code]

    def to_ascii(self):
        """Returns an ASCII representation of the barCode.
        :return type: String
        """
        code = self.build()
        for i, line in enumerate(code):
            code[i] = line.replace('1', '|').replace('0', ' ')
        return '\n'.join(code)


# Shortcuts
I2OF5 = Interleaved2of5
