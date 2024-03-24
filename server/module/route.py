
from module.config import conf


def route(config):

    config.add_static_view(name='html', path='html')


    config.add_route('api', '')
    # config.add_view(test.echo, route_name='api')

    config.scan()

    return config

