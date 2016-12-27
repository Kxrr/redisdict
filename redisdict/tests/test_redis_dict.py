# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
import uuid
import collections
import unittest

from redisdict.redisdict import SimpleRedisDict, ComplexRedisDict
from redisdict.exceptions import SerialisationError


class RedisDictTestCase(unittest.TestCase):
    klass = SimpleRedisDict
    name = 'dct'

    def setUp(self):
        self.klass(self.name, {}, autoclean=True)  # clean it up

    def test_delete(self):
        pass

    def test_resolve_options(self):
        pass


class SimpleRedisDictCase(RedisDictTestCase):
    klass = SimpleRedisDict

    def test_init_empty(self):
        self.klass(self.name, {})

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


class ComplexRedisDictCase(RedisDictTestCase):
    klass = ComplexRedisDict

    def test_init_empty(self):
        self.klass(self.name, {})

    def test_dict(self):
        origin = {
            'name': 'Jim',
            'birth': datetime.date.today(),
            'id': uuid.uuid4(),
        }

        cloud = self.klass(self.name, origin)

        for k, v in origin.items():
            self.assertEqual(v, cloud[k])
