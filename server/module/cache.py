import redis
import time

from module.config import conf
from module.config import redis_conf


class Cache(object):

    def __init__(self):
        mode = conf['mode']
        host = redis_conf[mode]
        res = host.split(':')
        if len(res) == 2:
        	host,port = res
        else:
        	host = res[0]
        	port = 6379

        # print("redis host=%s, port=%s  mode=%s" % (host,port,   mode))
        self.redis = redis.Redis(host=host, port=port, db=0)


    def set(self, key, value, expire=None):
        self.redis.set(key, value, expire)


    def get(self, key):
        return self.redis.get(key)

    def inc(self, key):
        return self.redis.incr(key)

    def clear(self, key):
        return self.redis.set(key,0)

    def delete(self, key):
        self.redis.delete(key)

    def push(self, key, val):
        self.redis.rpush(key, val)

    def list(self, key):
        return self.redis.lrange(key, 0, -1)

    def pop(self, key):
        return self.redis.rpop(key)
