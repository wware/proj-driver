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


class TodoError(NotImplementedError):
    pass


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

    for zi in range(1000000):   # die on StopIteration or instance.stop()
        z = 0.01 * zi
        outf = open('foo.rgb', 'w')
        generateRgb(z, stl, red, outf)
        outf.close()
        os.system(('convert -size {0}x{1} -alpha off -depth 8' +
                   ' foo.rgb cherrypy/static/image.png').format(W, H))
        os.system('echo "{0} {1}" > cherrypy/static/image.info'
                  .format(z, duration))
        # instance.after_layer()


if __name__ == '__main__':
    CherryPyServer.main()
