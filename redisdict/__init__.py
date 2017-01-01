# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

from .utils import connect_redis
from .exceptions import ConfigurationError

logging.basicConfig()
logger = logging.getLogger('redisdict')

VERSION = (0, 0, 3)
__version__ = '.'.join(map(str, VERSION))


class Configuration(object):
    def __init__(self):
        self.uri = None
        self.namespace = None
        self.connection_error_policy = None

        self._client = None

    @property
    def client(self):
        if self._client:
            return self._client
        else:
            if not self.uri:
                raise ConfigurationError('Uri or connection are required.')
            return connect_redis(self.uri)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k not in dir(self):
                logger.debug('no such configure {}'.format(k))
                continue

            private_k = '_' + k
            k = private_k if private_k in dir(self) else k

            setattr(self, k, v)


_config = Configuration()


def configure(uri='redis://127.0.0.1:6379/0', client=None, connection_error_policy=None):
    """
    :param uri: Redis uri
    :param client: Redis client(if provided together with ``uri`` , ``client`` will be used.)
    :param connection_error_policy:
    """
    _config.update(**locals())

configure()

from .redisdict import RedisDict, ComplexRedisDict, SimpleRedisDict


__all__ = ('RedisDict', 'SimpleRedisDict', 'ComplexRedisDict', 'configure', 'Configuration', 'logger')
