# -*- coding: utf-8 -*-
from __future__ import absolute_import

import redis
import urlparse
from collections import Mapping, defaultdict

VERSION = (0, 0, 1)
__version__ = '.'.join(map(str, VERSION))


def get_default_value(d):
    value = ''
    if isinstance(d, defaultdict):
        value = d.default_factory()
    return value


def connect_redis(uri):
    """
    Create a redis connection by uri.
    """
    puri = urlparse.urlparse(uri)
    host = puri.hostname
    port = puri.port
    password = puri.password if puri.password else ''
    db_name = puri.path.split('/')[1]
    r = redis.Redis(host=host, port=port, password=password, db=db_name)
    assert r.ping()
    return r


class RedisDict(Mapping):
    def __init__(self, name, d, autoclean=False, uri='redis://127.0.0.1:6379/0'):
        """
        :param name: Name to specific this object in Redis.
        :param d: The dict will map to Redis.
        :param autoclean: If delete the old object in Redis when initiating.
        :param uri: Redis uri.
        """
        self.name = name
        self._name = self.gen_name(self.name)
        self._origin = d.copy()
        self._r = connect_redis(uri)
        self._default_key = self.gen_name('default')

        if autoclean:
            self.del_all()

        self.map(self._origin)
        self._set_item(self._default_key, get_default_value(self._origin))

    @staticmethod
    def gen_name(name):
        return 'RedisDict:{}'.format(name)

    def __getitem__(self, item):
        return self._r.hget(self._name, key=item) or self._r.hget(self._name, key=self._default_key)

    def __setitem__(self, key, value):
        return self._set_item(key, value, force=True)

    def __delitem__(self, key):
        return self._r.hdel(self._name, key)

    def __len__(self):
        return self._r.hlen(self._name)

    def __iter__(self):
        return (key for key in self._r.hkeys(self._name) if key != self._default_key)

    def __contains__(self, item):
        return self._r.hexists(self._name, item)

    def _set_item(self, key, value, force=False):
        if force or (not self.__contains__(key)):
            self.check_value_type(value)
            return self._r.hset(self._name, key, value)
        return 0

    def _map(self, d, **kwargs):
        default_kw = {'force': False}
        default_kw.update(kwargs)
        return all([self._set_item(k, v, **default_kw) for k, v in d.iteritems()])

    def map(self, d=None, **options):
        """Grab the data from dict to Redis.
        :keyword force: if reset the value of key when the key exists in Redis, the default is set to False.
        """
        d = d or {}
        return self._map(d, **options)

    def del_all(self):
        """
        Delete this object in Redis.
        """
        return self._r.delete(self._name)

    @staticmethod
    def check_value_type(value):
        if isinstance(value, (type(None),)):
            raise ValueError('{0} is not supported.'.format(type(value)))

    def __str__(self):
        return '<{0}>'.format(self._name)


class AutoCleanRedisDict(RedisDict):
    def __init__(self, name, d):
        super(AutoCleanRedisDict, self).__init__(name, d, autoclean=True)
