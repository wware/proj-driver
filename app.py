#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
  CMD [-z <height>]
  CMD [-t <seconds>]
  CMD [-d <duration>] [--red | -r] [-s | --server]
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

import os.path
import cherrypy
import array
import docopt
import os
import string
import sys
import termios
import threading
import time
import tty

W, H = 1024, 768
duration = 1000


class Image(object):
    def __init__(self, z, scale=3):
        self.ary = array.array('B')
        self.ary.fromstring(3 * W * H * '\x00')
        self.scale = scale
        self.z = z

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

    def write(self):
        try:
            os.remove('foo.rgb')
        except:
            pass
        outf = open('foo.rgb', 'w')
        outf.write(self.ary.tostring())
        outf.close()
        os.system(('convert -size {0}x{1} -alpha off -depth 8' +
                   ' foo.rgb static/image.png').format(W, H))
        os.system('echo "{0} {1}" > static/image.info'
                  .format(self.z, duration))


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


img = None


class addPedestal(object):
    """
    >>> @addPedestal(0, 0)
    ... def f(z):
    ...     print z
    >>> for i in range(25):
    ...     f(i)
    This test needs work.
    """
    N = 10

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __call__(self, f):
        def inner(z, duration, color):
            if z < self.N:
                img.rectangle(0, 0, 3, 3, color)
                img.write()
                print 'pedestal', z
            else:
                f(z - self.N, duration, color)
        return inner


@addPedestal(0, 0)
def layer(z, duration=2000, color='\xff\xff\xff'):
    # print 'LAYER', z
    if z in range(0, 36):
        img.rectangle(-z, 0, 10, 7, color)
        img.rectangle(z, 0, 10, 7, color)
        img.rectangle(0, -z, 7, 10, color)
        img.rectangle(0, z, 7, 10, color)
    elif z in range(36, 40):
        img.rectangle(-z, 0, 10, 7, color)
        img.rectangle(z, 0, 10, 7, color)
        img.rectangle(0, -z, 7, 10, color)
        img.rectangle(0, z, 7, 10, color)
        img.hollow_diamond(0, 0, 40, 7, color)
    elif z in range(40, 43):
        img.rectangle(80 - z, 0, 10, 7, color)
        img.rectangle(z - 80, 0, 10, 7, color)
        img.rectangle(0, 80 - z, 7, 10, color)
        img.rectangle(0, z - 80, 7, 10, color)
        img.hollow_diamond(0, 0, 40, 7, color)
    elif z in range(43, 80):
        img.rectangle(80 - z, 0, 10, 7, color)
        img.rectangle(z - 80, 0, 10, 7, color)
        img.rectangle(0, 80 - z, 7, 10, color)
        img.rectangle(0, z - 80, 7, 10, color)
    else:
        CherryPyServer.stop()
    img.write()
    print 'z =', z


class CherryPyServer(threading.Thread):

    server_running = False

    def run(self):
        config = {
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir':
                    os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 'static')
            },
            '/': {
                'tools.template.on': True,
                'tools.template.template': 'index.html',
                # We must disable the encode tool because it
                # transforms our dictionary into a list which
                # won't be consumed by the jinja2 tool
                'tools.encode.on': False
            },
            'global': {
                'server.socket_port': 8090
            }
        }

        # Register the Jinja2 plugin
        from jinja2 import Environment, FileSystemLoader
        from jinja2plugin import Jinja2TemplatePlugin
        env = Environment(loader=FileSystemLoader('.'))
        Jinja2TemplatePlugin(cherrypy.engine, env=env).subscribe()

        # Register the Jinja2 tool
        from jinja2tool import Jinja2Tool
        cherrypy.tools.template = Jinja2Tool()

        cherrypy.quickstart(self, '', config=config)

    @cherrypy.expose
    def index(self):
        return {}

    @cherrypy.expose
    def image(self):
        return open('static/image.png', 'r').read()

    @cherrypy.expose
    def info(self):
        return open('static/image.info', 'r').read()

    @classmethod
    def stop(cls):
        if cls.server_running:
            cherrypy.engine.exit()
        raise SystemExit

    @classmethod
    def main(cls):
        global img, duration
        args = docopt.docopt(__doc__.replace('CMD', sys.argv[0]))
        if args['-s'] or args['--server']:
            server = cls()
            cls.server_running = True
            server.start()
        if args['-z']:
            z = string.atoi(args['<height>'])
            layer(z)
        elif args['-t']:
            secs = string.atoi(args['<seconds>'])
            for z in range(80):
                layer(z)
                time.sleep(secs)
        else:
            red = args['-r'] or args['--red']
            if red:
                color = '\xff\x00\x00'
            else:
                color = '\xff\xff\xff'
            duration = string.atoi(args['<duration>'])
            for z in range(1000):
                img = Image(z)
                layer(z, duration, color)
                while True:
                    ch = getch()
                    if ch in ('q', 'Q'):
                        cls.stop()
                        raise SystemExit
                    if ch in ('n', 'N'):
                        break


if __name__ == '__main__':
    CherryPyServer.main()
