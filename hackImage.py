#!/usr/bin/python

"""
Usage:
  CMD [-z <height>]
  CMD [-t <seconds>]
  CMD
"""

"""
Usage:
  CMD [-z <height>] [--view | -v]
  CMD [-t <seconds>] [--view | -v]
  CMD
"""

"""
It would be great to handle STL files. So you need some command line arguments:
    the STL filename
    the offsets and scale factors for x, y, and z
    the current z value

Then do something like this. In this case you'll be writing line by line and
won't need an "ary" for the entire image.

    for each yline
        create a triangle list
    for each triangle in the STL file
        transform triangle into correct coordinate space
        get ymin, ymax, zmin, zmax
        if zmin <= z <= zmax:
            for y in range(ymin, ymax):
                add triangle to triangle list for y
    open the output file
    for each yline
        create a point list
        for each triangle in this yline's triangle list
            compute intersection with this y and z value
            if intersection exists:
                if normal's x component > 0:
                    add a "begin" point to the point list
                elif normal's x component < 0:
                    add an "end" point to the point list
        sort point list by x coordinate
        create a pixel array initialized to black
        for each contiguous begin/end pair:
            do a white run in pixel array
        write pixel array to the output file
    close the output file
"""

import array
import docopt
import os
import string
import sys
import termios
import time
import tty

W, H = 1280, 720


class Image(object):
    def __init__(self, scale=3):
        self.ary = array.array('B')
        self.ary.fromstring(3 * W * H * '\x00')
        self.scale = scale

    def run(self, x1, x2, y, color='\xff\xff\xff'):
        assert x1 <= x2
        if x1 == x2:
            return
        assert 0 <= x1 < W
        assert 0 <= x2 < W
        assert 0 <= y < H
        begin = 3 * (W * y + x1)
        end = 3 * (W * y + x2)
        middle = array.array('B')
        middle.fromstring((x2 - x1) * color)
        self.ary = self.ary[:begin] + middle + self.ary[end:]

    def rectangle(self, xcenter, ycenter, xsize, ysize, color='\xff\xff\xff'):
        if self.scale is not None:
            xcenter = int((W / 2) + self.scale * xcenter)
            ycenter = int((H / 2) - self.scale * ycenter)   # intentional
            xsize *= self.scale
            ysize *= self.scale
        xsize = int(xsize)
        ysize = int(ysize)
        xsize2 = xsize / 2
        ysize2 = ysize / 2
        for i in range(ysize):
            self.run(xcenter - xsize2,
                     xcenter + xsize2,
                     (ycenter - ysize2) + i,
                     color)

    def circle(self, xcenter, ycenter, radius, color='\xff\xff\xff'):
        if self.scale is not None:
            xcenter = int((W / 2) + self.scale * xcenter)
            ycenter = int((H / 2) - self.scale * ycenter)   # intentional
            radius = self.scale * radius
        for y in range(int(ycenter - radius - 1), int(ycenter + radius + 1)):
            d = radius**2 - (y - ycenter)**2
            if d >= 0:
                self.run(int(xcenter - d**0.5),
                         int(xcenter + d**0.5),
                         y,
                         color)

    def hollow_diamond(self, xcenter, ycenter, size, width,
                       color='\xff\xff\xff'):
        if self.scale is not None:
            xcenter = int((W / 2) + self.scale * xcenter)
            ycenter = int((H / 2) - self.scale * ycenter)   # intentional
            size *= self.scale
            width *= self.scale
        for i in range(int(width)):
            y = int(ycenter - size) + i
            self.run(xcenter - i, xcenter + i, y, color)
        for i in range(int(size - width)):
            y = int(ycenter + width - size) + i
            self.run(xcenter - width - i, xcenter - i, y, color)
            self.run(xcenter + i, xcenter + width + i, y, color)
        for i in range(int(size - width)):
            y = ycenter + i
            self.run(xcenter - size + i, xcenter - size + width + i, y, color)
            self.run(xcenter + size - width - i, xcenter + size - i, y, color)
        for i in range(int(width)):
            y = int(ycenter + size - width) + i
            self.run(xcenter - width + i, xcenter + width - i, y, color)

    def write(self, filename):
        outf = open(filename, 'w')
        outf.write(self.ary.tostring())
        outf.close()


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def layer(z, view=False):
    img = Image()
    if z in range(0, 36):
        img.rectangle(-z, 0, 10, 7)
        img.rectangle(z, 0, 10, 7)
        img.rectangle(0, -z, 7, 10)
        img.rectangle(0, z, 7, 10)
    elif z in range(36, 40):
        img.rectangle(-z, 0, 10, 7)
        img.rectangle(z, 0, 10, 7)
        img.rectangle(0, -z, 7, 10)
        img.rectangle(0, z, 7, 10)
        img.hollow_diamond(0, 0, 40, 7)
    elif z in range(40, 43):
        img.rectangle(80 - z, 0, 10, 7)
        img.rectangle(z - 80, 0, 10, 7)
        img.rectangle(0, 80 - z, 7, 10)
        img.rectangle(0, z - 80, 7, 10)
        img.hollow_diamond(0, 0, 40, 7)
    elif z in range(43, 80):
        img.rectangle(80 - z, 0, 10, 7)
        img.rectangle(z - 80, 0, 10, 7)
        img.rectangle(0, 80 - z, 7, 10)
        img.rectangle(0, z - 80, 7, 10)
    img.write('foo.rgb')
    os.system(('convert -size {0}x{1} -alpha off -depth 8' +
               ' foo.rgb static/image.png').format(W, H))
    # if view:
    #     os.system('open static/image.png')
    os.system ('echo "{0} {1}" > static/image.info'.format(z, 2000))
    print 'z =', z


def main():
    args = docopt.docopt(__doc__.replace('CMD', sys.argv[0]))
    # view = args['-v'] or args['--view']
    view = False
    # import pprint
    # pprint.pprint(args)
    if args['-z']:
        z = string.atoi(args['<height>'])
        layer(z, view)
    elif args['-t']:
        secs = string.atoi(args['<seconds>'])
        for z in range(80):
            layer(z, False)
            time.sleep(secs)
    else:
        for z in range(80):
            layer(z, view)
            while True:
                ch = getch()
                if ch in ('q', 'Q'):
                    raise SystemExit
                if ch in ('n', 'N'):
                    break


if __name__ == '__main__':
    main()
