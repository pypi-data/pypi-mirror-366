import cherrypy
from importlib.metadata import version
from os import environ
from platform import python_version
from posixpath import join

from finitelycomputable.finitelycomputable_env_info import (
    base_path, env_html, include_app, index_html,
)


version_text = environ.get('MICROSITES_VERSION_TEXT', '')
base_path = join('/', environ.get('BASE_PATH', ''))

class Root(object):
    @cherrypy.expose
    def index(self):
        return index_html('CherryPy framework (mount method)', __name__)

    @cherrypy.expose
    def env_info(self):
        return env_html('CherryPy', __name__)


def setup_server():
    # because CherryPy and only Cherrypy needs to instantiate its own singletons
    cherrypy.tree.__module__ = __name__
    try:
        app_path = join(base_path,'hello_world/')
        module = include_app("helloworld_cherrypy", app_path)
        cherrypy.tree.mount(
                module.HelloWorld(), app_path, {'/': {}})
    except ModuleNotFoundError:
        pass
    cherrypy.tree.mount(Root(), join(base_path, '/'), {'/': {}})
    return cherrypy.tree


application = setup_server()


def run():
    from sys import argv, exit, stderr
    if len(argv) < 2 or argv[1] != 'run':
        stderr.write(f'usage: {argv[0]} run [port]\n')
        exit(1)
    try:
        cherrypy.config.update({'server.socket_port': int(argv[2])})
    except IndexError:
        pass
    cherrypy.engine.start()
    cherrypy.engine.block()
