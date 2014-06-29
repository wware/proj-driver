# -*- coding: utf-8 -*-
import os.path
import random
import string
import cherrypy

class Root(object):

    @cherrypy.expose
    def index(self):
        return {}

    # if these are exposed via static, they'll be cached, and changes won't propogate
    @cherrypy.expose
    def image(self):
        return open('static/image.png', 'r').read()

    # if these are exposed via static, they'll be cached, and changes won't propogate
    @cherrypy.expose
    def info(self):
        return open('static/image.info', 'r').read()

if __name__ == '__main__':
    config = {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
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

    cherrypy.quickstart(Root(), '', config=config)
