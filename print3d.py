#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
  CMD [-T | --test] [-D | --debug]
  CMD [-d <duration>] [--red | -r] [-s | --server] [-D | --debug] --stl=<STLFILE>
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
import logging

logger = logging.getLogger('Arduino stepper control')
ch = logging.StreamHandler()
ch.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - " +
                      "%(levelname)s - %(message)s")
)
logger.addHandler(ch)

from stl import generateRgb, Stl

W, H = 1024, 768

WHITE = '\xff\xff\xff'
RED = '\xff\x00\x00'

SCALE = 3


class AbstractMethodError(NotImplementedError):
    pass


class TodoError(NotImplementedError):
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

    def write(self, z, duration):
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
        pass

    def layer(self, z, img, color=WHITE):
        outf = open(img, 'w')
        generateRgb(z, self.stl, red, outf)

    def after_layer(self):
        """
        Wait for the projector to say it's done - needs new CherryPy endpoint
        Turn the stepper to lower the product one increment into the liquid
        """
        raise TodoError("wait for projector to be finished")
        stepper.steps(-36)

    @classmethod
    def main(cls):
        args = docopt.docopt(__doc__.replace('CMD', sys.argv[0]))

        if args['-D'] or args['--debug']:
            logger.setLevel(logging.DEBUG)

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

        red = (args['-r'] or args['--red'])

        if args['-d']:
            duration = string.atoi(args['<duration>'])
        else:
            duration = 1000

        assert args['--stl'], __doc__
        stl = Stl(args['--stl'])

        # instance.build_supports(color)
        for zi in range(1000000):   # die on StopIteration or instance.stop()
            z = 0.01 * zi
            outf = open('foo.rgb', 'w')
            generateRgb(z, stl, red, outf)
            outf.close()
            os.system(('convert -size {0}x{1} -alpha off -depth 8' +
                       ' foo.rgb static/image.png').format(W, H))
            os.system('echo "{0} {1}" > static/image.info'
                      .format(z, duration))
            instance.after_layer()


if __name__ == '__main__':
    CherryPyServer.main()
