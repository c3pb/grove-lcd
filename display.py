#!/usr/local/bin/python2.7

import argparse
import math
import sys
import time

use_dummy = False
try:
    from smbus import SMBus
except ImportError:
    use_dummy = True

if not use_dummy:
    import backlight
    import screen

class Display(object):
    backlight = None
    screen    = None

    def __init__(self):
        self.dummy = use_dummy
        if use_dummy:
            self.pos  = (0, 0)
            self.rows = [ " " * 16, " " * 16 ]
            sys.stdout.write(chr(0x1b) + "[2J")
            sys.stdout.flush()
        else:
            self.bus = SMBus(1)
            self.backlight = backlight.Backlight(self.bus, 0x62)
            self.screen    = screen.Screen(self.bus, 0x3e)

    def write(self, text):
        if use_dummy:
            t  = self.rows[self.pos[1]][:self.pos[0]]
            t += text
            t += self.rows[self.pos[1]][-(16 - len(text) - self.pos[0]):]
            self.rows[self.pos[1]] = t[0:16]
            self.redraw()
        else:
            self.screen.write(text)

    def color(self, r, g, b):
        assert r >= 0 and r < 256
        assert g >= 0 and g < 256
        assert b >= 0 and b < 256
        if use_dummy:
            f = 43.0
            n = (int(r / f) * 36) + (int(g / f) * 6) + int(b / f) + 16
            sys.stdout.write(chr(0x1b) + "[48;5;" + str(n) + "m")
            self.redraw()
        else:
            self.backlight.set_color(r, g, b)

    def move(self, col, row):
        assert row == 0 or row == 1
        assert col >= 0 and col < 16
        if use_dummy:
            self.pos = (col, row)
        else:
            self.screen.setCursor(col, row)

    def updatecursor(self, col, row):
        if use_dummy:
            sys.stdout.write(chr(0x1b) + "[" + str(row) + ";" + str(col) + "H")
        else:
            raise NotImplemented

    def redraw(self):
        if use_dummy:
            self.updatecursor(0, 0)
            sys.stdout.write("{:<16}\n{:<16}\n".format(self.rows[0], self.rows[1]))
            sys.stdout.flush()
        else:
            raise NotImplemented

def demo(d):
    d.move(0, 0)
    d.write("Yeah.      Nice.")

    cnt = 0
    while True:
        r = int((math.sin(cnt) + 1) * 128)
        g = int((math.sin(cnt + 0.75 * math.pi) + 1) * 128)
        b = int((math.sin(cnt + 1.5 * math.pi) + 1) * 128)

        d.color(r, g, b)

        d.move(0, 1)
        d.write(" {:>3}  {:>3}   {:>3}".format(r, g, b))

        if use_dummy:
            cnt += 0.25
        else:
            cnt += 0.01
        time.sleep(0.01)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Driver for Grove-LCD display boards")

    parser.add_argument("-demo", default=False, dest="demo", action="store_true", help="run demo")
    parser.add_argument("text", metavar="TEXT", type=str, nargs="*", help="String to display")
    parser.add_argument("-r", default=255, dest="red", metavar="RED", type=int, help="red component of backlight color [0-255]")
    parser.add_argument("-g", default=255, dest="green", metavar="GREEN", type=int, help="green component of backlight color [0-255]")
    parser.add_argument("-b", default=255, dest="blue", metavar="BLUE", type=int, help="blue component of backlight color [0-255]")

    args = parser.parse_args()

    if args.demo:
        d = Display()
        demo(d)
        sys.exit(0)

    failed = False

    if args.red < 0 or args.red > 255:
        failed = True
    if args.green < 0 or args.green > 255:
        failed = True
    if args.blue < 0 or args.blue > 255:
        failed = True

    if len(args.text) == 0:
        failed = True
    if len(args.text) > 2:
        failed = True

    if failed:
        parser.print_usage()
        sys.exit(-1)

    d = Display()
    d.color(args.red, args.green, args.blue)
    d.move(0, 0)
    d.write(args.text[0])
    if len(args.text) == 2:
        d.move(0, 1)
        d.write(args.text[1])
