# from module.cache import Cache
from pyramid.response import Response


def echo(request):

    return Response('API V 1.0')
