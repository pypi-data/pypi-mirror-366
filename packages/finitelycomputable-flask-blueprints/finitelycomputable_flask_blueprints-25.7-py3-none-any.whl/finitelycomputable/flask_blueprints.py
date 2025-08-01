from flask import Flask, cli
from os import environ
from posixpath import join

from finitelycomputable.finitelycomputable_env_info import (
    base_path, env_html, include_app, index_html,
)


application = Flask(__name__)

@application.route(join(base_path, '/'))
def index():
    return index_html('Flask framework (blueprint method)', __name__)

@application.route(join(base_path, 'env_info/'))
@application.route(join(base_path, 'env_info'))
def env_info():
    return env_html('Flask', __name__)

try:
    app_path = join(base_path, 'hello_world')
    module = include_app("helloworld_flask", app_path)
    application.register_blueprint(module.blueprint, url_prefix=app_path)
except ModuleNotFoundError:
    pass

try:
    app_path = join(base_path, 'identification_of_trust')
    module = include_app("idtrust_app_flask", app_path)
    application.register_blueprint(module.blueprint, url_prefix=app_path)
except ModuleNotFoundError:
    pass

def run():
    from sys import argv, exit, stderr
    usage = f'usage: {argv[0]} run|routes [port]\n'
    if len(argv) < 2:
        stderr.write(usage)
        exit(1)
    if argv[1] == 'run':
        try:
            port=int(argv[2])
        except IndexError:
            port=8080
        application.run(port=port)
    else:
        environ['FLASK_APP'] = __name__
        stderr.write(environ['FLASK_APP'])
        cli.main()
