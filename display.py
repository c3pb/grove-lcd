#!/usr/local/bin/python2.7

import math
import time
import sys

use_dummy = False
try:
    from smbus import SMBus
except ImportError:
    print("Couldn't import smbus bindings, using dummy display")
    use_dummy = True

if not use_dummy:
    import backlight
    import screen

class Display(object):
    backlight = None
    screen = None

    def __init__(self, bus):
        self.backlight = backlight.Backlight(bus, 0x62)
        self.screen    = screen.Screen(bus, 0x3e)

    def write(self, text):
        self.screen.write(text)

    def color(self, r, g, b):
        self.backlight.set_color(r, g, b)

    def move(self, col, row):
        self.screen.setCursor(col, row)

class DummyDisplay(object):
    def __init__(self, bus=None):
        self.pos  = (0, 0)
        self.rows = [ " " * 16, " " * 16 ]
        sys.stdout.write(chr(0x1b) + "[2J")
        sys.stdout.flush()

    def write(self, text):
        t  = self.rows[self.pos[1]][:self.pos[0]]
        t += text
        t += self.rows[self.pos[1]][-(16 - len(text) - self.pos[0]):]
        self.rows[self.pos[1]] = t[0:16]
        self.redraw()

    def color(self, r, g, b):
        f = 43.0
        assert r >= 0 and r < 256
        assert g >= 0 and g < 256
        assert b >= 0 and b < 256
        n = (int(r / f) * 36) + (int(g / f) * 6) + int(b / f) + 16
        sys.stdout.write(chr(0x1b) + "[48;5;" + str(n) + "m")
        self.redraw()

    def move(self, col, row):
        assert row == 0 or row == 1
        assert col >= 0 and col < 16
        self.pos = (col, row)

    def updatecursor(self, col, row):
        sys.stdout.write(chr(0x1b) + "[" + str(row) + ";" + str(col) + "H")

    def redraw(self):
        self.updatecursor(0, 0)
        sys.stdout.write("{}\n{}".format(self.rows[0], self.rows[1]))
        sys.stdout.flush()
        pass

if __name__ == "__main__":
    d = None
    if use_dummy:
        d = DummyDisplay()
        pass
    else:
        d = Display(SMBus(1))
    d.move(0, 0)
    d.write("Yeah.      Nice.")

    cnt = 0
    while True:
        r = int((math.sin(cnt) + 1) * 128)
        g = int((math.sin(cnt + 0.75 * math.pi) + 1) * 128)
        b = int((math.sin(cnt + 1.5 * math.pi) + 1) * 128)

        d.color(r, g, b)

        # d.move(0, 1)
        # d.write("{:>3} {:>3} {:>3}".format(r, g, b))

        if use_dummy:
            cnt += 0.25
        else:
            cnt += 0.01
        time.sleep(0.01)
