#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import array
import os


W, H = 1024, 768

WHITE = '\xff\xff\xff'
RED = '\xff\x00\x00'

SCALE = 3


class Image(object):
    def __init__(self, scale=SCALE):
        self.ary = array.array('B')
        self.ary.fromstring(3 * W * H * '\x00')
        self.scale = scale

    def run(self, x1, x2, y, color=WHITE):
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

    def rectangle(self, xcenter, ycenter, xsize, ysize, color=WHITE):
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

    def circle(self, xcenter, ycenter, radius, color=WHITE):
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
                       color=WHITE):
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

    def write(self, z, duration):
        outf = open('foo.rgb', 'w')
        outf.write(self.ary.tostring())
        outf.close()
        os.system(('convert -size {0}x{1} -alpha off -depth 8' +
                   ' foo.rgb cherrypy/static/image.png').format(W, H))
        os.system('echo "{0} {1}" > cherrypy/static/image.info'
                  .format(z, duration))
