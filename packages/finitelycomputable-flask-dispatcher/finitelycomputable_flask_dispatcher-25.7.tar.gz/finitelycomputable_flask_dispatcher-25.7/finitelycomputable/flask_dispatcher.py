from flask import Flask
from importlib.metadata import version
from os import environ
from platform import python_version
from posixpath import join
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from finitelycomputable.finitelycomputable_env_info import (
    base_path, env_html, include_app, index_html,
)


application = Flask(__name__)
base_path = join('/', environ.get('BASE_PATH', ''))
version_text = environ.get('MICROSITES_VERSION_TEXT', '')
included_apps = []


@application.route(join(base_path, '/'))
def index():
    return index_html('Flask framework (dispatcher method)', __name__)

@application.route(join(base_path, 'env_info/'))
@application.route(join(base_path, 'env_info'))
def env_info():
    return env_html('Flask', __name__)


hello_path = join(base_path, 'hello_world')
try:
    hello_module = include_app("helloworld_flask", hello_path)
except ModuleNotFoundError:
    try:
        hello_module = include_app("helloworld_falcon", hello_path)
    except ModuleNotFoundError:
        try:
            hello_module = include_app("helloworld_morepath", hello_path)
        except ModuleNotFoundError:
            try:
                environ['BASE_PATH'] = hello_path
                hello_module = include_app("helloworld_cherrypy", hello_path)
            except ModuleNotFoundError:
                environ['BASE_PATH'] = base_path
idtrust_path = join(base_path, 'identification_of_trust')
try:
    idtrust_module = include_app("idtrust_app_flask", idtrust_path)
except ModuleNotFoundError:
    try:
        idtrust_module = include_app("idtrust_app_falcon", idtrust_path)
    except ModuleNotFoundError:
        pass

dispatch_map = {}
if 'hello_module' in locals():
    dispatch_map[hello_path] = hello_module.application
if 'idtrust_module' in locals():
    dispatch_map[idtrust_path] = idtrust_module.application
application.wsgi_app = DispatcherMiddleware(application.wsgi_app, dispatch_map)


def run():
    from sys import argv, exit, stderr
    if len(argv) < 2 or argv[1] != 'run':
        stderr.write(f'usage: {argv[0]} run [port]\n')
        exit(1)
    try:
        port=int(argv[2])
    except IndexError:
        port=8080
    application.run(port=port)
