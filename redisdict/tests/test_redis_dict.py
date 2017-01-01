# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
import redis
import datetime
import uuid
import collections
import unittest

from redisdict.redisdict import SimpleRedisDict, ComplexRedisDict, _config
from redisdict.exceptions import SerialisationError
from redisdict import configure

logger = logging.getLogger('redisdict')
logger.setLevel(logging.DEBUG)


class _RedisDictTestCase(unittest.TestCase):
    klass = SimpleRedisDict
    name = 'dct'

    def setUp(self):
        self.klass(self.name, {}, autoclean=True)  # clean it up

    def test_init_empty(self):
        self.klass(self.name, {})

    def test_key_not_exist(self):
        cloud = self.klass(self.klass, {'name': 'Jim'})
        cloud['name']
        with self.assertRaises(KeyError):
            cloud['age']

    def test_delete(self):
        pass

    def test_resolve_options(self):
        pass


class SimpleRedisDictCase(_RedisDictTestCase):
    klass = SimpleRedisDict

    def test_dict(self):
        origin = {
            'name': 'Jim',
            'age': 5,
        }

        cloud = SimpleRedisDict(self.klass, origin)

        for k, v in origin.items():
            value_in_cloud = cloud[k]
            self.assertIsInstance(value_in_cloud, str)
            self.assertEqual(value_in_cloud, str(v))

    def test_raise_error(self):
        with self.assertRaises(SerialisationError):
            self.klass(self.name, {'name': None})

    def test_with_default_dict(self):
        v = 'value of default dict'
        dct = collections.defaultdict(lambda: v)
        cloud = self.klass(self.name, dct)
        self.assertEqual(cloud[str(uuid.uuid4())], v)

    def test_lock(self):
        cloud = self.klass(self.name, {})
        with cloud.Lock():
            cloud['info'] = 'blah blah'


class ComplexRedisDictCase(_RedisDictTestCase):
    klass = ComplexRedisDict

    def test_dict(self):
        origin = {
            'name': 'Jim',
            'birth': datetime.date.today(),
            'id': uuid.uuid4(),
            'address': None,
        }

        cloud = self.klass(self.name, origin)

        for k, v in origin.items():
            self.assertEqual(v, cloud[k])


class ConfigTestCase(unittest.TestCase):

    def test_configure_client(self):
        client = redis.Redis()
        configure(client=client)
        self.assertIs(client, _config.client)

