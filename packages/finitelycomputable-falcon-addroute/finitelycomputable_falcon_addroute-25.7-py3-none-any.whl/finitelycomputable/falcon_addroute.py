import falcon
from os import environ
from posixpath import join

from finitelycomputable.finitelycomputable_env_info import (
    base_path, env_html, include_app, index_html,
)


class Index(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_HTML
        resp.text = index_html('Falcon framework (addroute method)', __name__)


class EnvInfo(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_HTML
        resp.text = env_html('falcon', __name__)


def add_routes(application, base_path):
    application.add_route(base_path, Index())
    application.add_route(join(base_path, 'env_info'), EnvInfo())

application = falcon.App(media_type=falcon.MEDIA_HTML)
application.req_options.strip_url_path_trailing_slash = True
add_routes(application, base_path)

try:
    app_path = join(base_path, 'hello_world')
    module = include_app("helloworld_falcon", app_path)
    module.add_routes(application, app_path)
except ModuleNotFoundError:
    pass

try:
    app_path = join(base_path, 'identification_of_trust')
    module = include_app("idtrust_app_falcon", app_path)
    module.add_routes(application, app_path)
except ModuleNotFoundError:
    pass

def run():
    from sys import argv, exit, stderr
    usage = f'usage: {argv[0]} run [port]\n'
    if len(argv) < 2:
        stderr.write(usage)
        exit(1)
    if argv[1] == 'run':
        from wsgiref import simple_server
        try:
            port=int(argv[2])
        except IndexError:
            port=8080
        simple_server.make_server('0.0.0.0', port, application).serve_forever()
    else:
        stderr.write(usage)
        exit(1)
