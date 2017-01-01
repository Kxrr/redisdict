#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import

import cPickle
from collections import Mapping, defaultdict

from . import logger, _config
from .utils import mutex
from .exceptions import SerialisationError


class SimpleRedisDict(Mapping):
    """ Simple Redis dict only accepts values of string types. """

    def __init__(self, name, dct,  **kwargs):
        """
        :param name: Name to specific this object in Redis.
        :param dct: The dict will map to Redis.
        :type dct: dict

        :param autoclean: If sets to False, will keep the existing key in redis hash, then mapping the others.
                          If sets to True, with delete the old redis hash first, then start mapping.
                          Default is **True** .

        """
        self.name = name

        self._name = self.generate_key_name(self.name)
        self._dct = dct.copy()
        self._client = _config.client
        self._default_key = self.generate_key_name('default')
        self._is_default_dict = False

        self.resolve_options(kwargs)

        for key, value in self._dct.items():
            self.setitem(key, value, force=False)

        if isinstance(self._dct, defaultdict):
            self._is_default_dict = True
            self.setitem(self._default_key, self._dct.default_factory())

        self.after_init()

    def after_init(self):
        pass

    def resolve_options(self, options):
        autoclean = options.pop('autoclean', True)
        if autoclean:
            self.clear()

    @classmethod
    def generate_key_name(cls, name):
        prefix = cls.__name__ + ':'
        return '{0}{1}'.format(prefix, name)

    @classmethod
    def dumps(cls, obj):
        if obj is None:
            raise SerialisationError('NoneType is not supported in {}'.format(cls.__name__))
        if not isinstance(obj, basestring):
            logger.warning("{0} => {1} will be converting to <type 'str'>".format(obj, type(obj)))
        return str(obj)

    @classmethod
    def loads(cls, b):
        return b

    def setitem(self, key, value, force=False):
        if (key not in self) or force:
            return bool(self._client.hset(self._name, key, self.dumps(value)))
        return False

    def getitem(self, key):
        value = self._client.hget(self._name, key=key)
        return self.loads(value)

    def clear(self):
        """
        Delete this object in Redis.
        """
        return self._client.delete(self._name)

    def __getitem__(self, key):
        if (key not in self) and (not self._is_default_dict):
            raise KeyError(key)
        return self.getitem(key) or self.get(self._default_key)

    def __setitem__(self, key, value):
        return self.setitem(key, value, force=True)

    def __delitem__(self, key):
        return self._client.hdel(self._name, key)

    def __len__(self):
        return self._client.hlen(self._name)

    def __iter__(self):
        return (key for key in self._client.hkeys(self._name) if key != self._default_key)

    def __contains__(self, item):
        return self._client.hexists(self._name, item)

    def __str__(self):
        return '<{0}>'.format(self._name)

    def Lock(self):
        name = '_LOCK_{0}'.format(self._name)
        return mutex(self._client, name)


class ComplexRedisDict(SimpleRedisDict):

    @classmethod
    def dumps(cls, obj):
        return cPickle.dumps(obj)

    @classmethod
    def loads(cls, b):
        return cPickle.loads(b)


RedisDict = SimpleRedisDict
