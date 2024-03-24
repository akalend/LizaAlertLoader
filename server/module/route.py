
from module.config import conf
from module import version
# import module.version


def route(config):

    config.add_static_view(name='html', path='html')

    config.add_route('api', '/')
    config.add_view(version.echo, route_name='api')

    config.scan()

    return config

