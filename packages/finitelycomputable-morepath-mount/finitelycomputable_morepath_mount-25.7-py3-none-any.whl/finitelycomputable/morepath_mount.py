import morepath
from os import environ
from posixpath import join

from finitelycomputable.finitelycomputable_env_info import (
    base_path, env_html, include_app, index_html,
)


class CoreApp(morepath.App):
    pass

@CoreApp.path(path=base_path)
class Root(object):
    pass

@CoreApp.html(model=Root)
def index(self, request):
    return index_html('Morepath framework (mount method)', __name__)

@CoreApp.html(model=Root, name='env_info')
def env_info(self, request):
    return env_html('morepath', __name__)

try:
    app_path = join(base_path, 'hello_world')
    module = include_app("helloworld_morepath", app_path)
    @CoreApp.mount(path=app_path, app=module.HelloWorldApp)
    def mount_hello_world():
        return module.HelloWorldApp()
except ModuleNotFoundError:
    pass


application = CoreApp()


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
        morepath.run(application, ignore_cli=True, port=port)
    elif argv[1] == 'routes':
        import dectate
        for app in application.commit():
            for view in dectate.query_app(app, 'view'):
                print(view[0].key_dict())
    else:
        stderr.write(usage)
        exit(1)
