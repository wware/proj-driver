#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
  CMD [-d <duration>] [--red | -r] [-s | --server] [-T | --test] [-D | --debug]
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
import tty

W, H = 1024, 768
duration = 1000

WHITE = '\xff\xff\xff'
RED = '\xff\x00\x00'

SCALE = 3


class AbstractMethodError(NotImplementedError):
    pass


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

    def write(self, z):
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
                  .format(z, duration))


class CherryPyServer(threading.Thread):

    server_running = False

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

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

    def stop(self):
        if self.server_running:
            cherrypy.engine.exit()
        raise SystemExit

    def build_supports(self, color):
        for z in range(-20, 0):
            img = Image()
            for x, y in self.supports():
                img.rectangle(x, y, 3, 3, color)
            img.write(z)
            self.after_layer()

    def supports(self):
        raise AbstractMethodError

    def layer(self, z, img, duration=2000, color=WHITE):
        raise AbstractMethodError

    def after_layer(self):
        def getch():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

        while True:
            ch = getch()
            if ch in ('q', 'Q'):
                self.stop()
                raise SystemExit
            if ch in ('n', 'N'):
                break

    @classmethod
    def main(cls):
        global duration

        args = docopt.docopt(__doc__.replace('CMD', sys.argv[0]))

        if args['-T'] or args['--test']:
            import doctest
            # verbose=True can be useful
            failure_count, test_count = \
                doctest.testmod(optionflags=doctest.ELLIPSIS)
            sys.exit(failure_count)

        instance = cls()
        if args['-s'] or args['--server']:
            instance.server_running = True
            instance.start()

        if args['-r'] or args['--red']:
            color = RED
        else:
            color = WHITE

        duration = string.atoi(args['<duration>'])

        instance.build_supports(color)
        for z in range(1000):   # die on StopIteration or instance.stop()
            img = Image()
            instance.layer(z, img, duration, color)
            instance.after_layer()
            img.write(z)
            print z


if __name__ == '__main__':
    CherryPyServer.main()
