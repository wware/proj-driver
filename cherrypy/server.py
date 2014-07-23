#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
  CMD [-D | --debug] (-T | --test)
  CMD [-d <duration>] [--red | -r] [-s | --server] \
[-D | --debug] --stl=<STLFILE>
"""

import os.path
import cherrypy
import docopt
import os
import sys
import threading
import logging

logger = logging.getLogger('Arduino stepper control')
ch = logging.StreamHandler()
ch.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - " +
                      "%(levelname)s - %(message)s")
)
logger.addHandler(ch)

W, H = 1024, 768

WHITE = '\xff\xff\xff'
RED = '\xff\x00\x00'

SCALE = 3


class AbstractMethodError(NotImplementedError):
    pass


class TodoError(NotImplementedError):
    pass


index_html = """<html>
<head><script src="jquery" type="text/javascript"></script></head>
<body style="background-color: #000000;">
<image id="myimage" style="display: none;"></image>
<script type="text/javascript">
$(function() {
    var lastId = null;
    var pingServer = function() {
        var refreshIntervalId = setInterval(function() {
            $.ajax('/info').success(
                function(value) {
                    var values = $.map(value.trim().split(' '), function(value) {
                        return parseInt(value);
                    });
                    var currentId = values[0];
                    var milliseconds = values[1];
                    console.log(values);
                    if (currentId == lastId) return;
                    clearInterval(refreshIntervalId);
                    lastId = currentId;
                    $('#myimage').attr('src', '/image');
                    $('#myimage').attr('style', 'display: block;');
                    setTimeout(function() {
                        $('#myimage').attr('style', 'display: none;');
                        pingServer();
                    }, milliseconds);
                }
            );
        }, 500);
    };
    pingServer();
});
</script>
</body>
</html>"""

class CherryPyServer(threading.Thread):

    server_running = False

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        config = {
            'global': {
                'server.socket_port': 8090
            }
        }

        cherrypy.quickstart(self, '', config=config)

    @cherrypy.expose
    def index(self):
        return index_html

    @cherrypy.expose
    def jquery(self):
        return open('../venv/lib/python2.7/site-packages/js/jquery/resources/jquery.js').read()

    @cherrypy.expose
    def image(self):
        return open('image.png', 'r').read()

    @cherrypy.expose
    def info(self):
        return open('image.info', 'r').read()

    def stop(self):
        if self.server_running:
            cherrypy.engine.exit()
        raise SystemExit


if __name__ == '__main__':
    def main():
        args = docopt.docopt(__doc__.replace('CMD', sys.argv[0]))

        if args['-D'] or args['--debug']:
            logger.setLevel(logging.DEBUG)

        if args['-T'] or args['--test']:
            import doctest
            # verbose=True can be useful
            failure_count, test_count = \
                doctest.testmod(optionflags=doctest.ELLIPSIS)
            sys.exit(failure_count)

        instance = CherryPyServer()
        if args['-s'] or args['--server']:
            instance.server_running = True
            instance.run()

        """
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
                       ' foo.rgb image.png').format(W, H))
            os.system('echo "{0} {1}" > image.info'
                      .format(z, duration))
            instance.after_layer()
        """
    main()
