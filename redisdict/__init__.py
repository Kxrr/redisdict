# -*- coding: utf-8 -*-
from __future__ import absolute_import

from collections import Mapping
from numbers import Number

from redisdict.utils import connect_redis, get_default_value, mutex

VERSION = (0, 0, 1)
__version__ = '.'.join(map(str, VERSION))


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

    @classmethod
    def get_connection(cls, uri):
        return connect_redis(uri)

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
        if not isinstance(value, (Number, basestring)):
            raise ValueError('{0} is not supported.'.format(type(value)))

    def Lock(self, expire):
        """
        :type expire: int
        """
        name = '_LOCK_{0}'.format(self._name)
        return mutex(self._r, name, expire)

    def __str__(self):
        return '<{0}>'.format(self._name)


class AutoCleanRedisDict(RedisDict):
    def __init__(self, name, d):
        super(AutoCleanRedisDict, self).__init__(name, d, autoclean=True)
