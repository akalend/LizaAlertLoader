
from module.config import conf
from module import version
from module import upload
# import module.version


def route(config):

    config.add_static_view(name='html', path='html')

    config.add_route('api', '/')
    config.add_view(version.echo, route_name='api')

    config.add_route('upload', 'upload/{uid}')
    config.add_view(upload.upload, route_name='upload')

    config.add_route('finish', 'upload/{uid}/finish')
    config.add_view(upload.finish, route_name='finish')



    config.scan()

    return config

