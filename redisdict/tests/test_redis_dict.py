# -*- coding: utf-8 -*-
import uuid
import collections
import unittest

from redisdict import RedisDict, AutoCleanRedisDict


class ImmutableDict(dict):
    def __setitem__(self, key, value):
        raise ValueError

    def __delitem__(self, key):
        raise ValueError


class TestRedisDict(unittest.TestCase):
    _data = ImmutableDict(price='$123')

    def test_init_empty(self):
        AutoCleanRedisDict('data', {})

    def test_get_key(self):
        data = AutoCleanRedisDict('data', self._data)
        self.assertEqual(data['price'], self._data['price'])
        self.assertEqual(data.get('price'), self._data['price'])

    def test_set_key(self):
        data = AutoCleanRedisDict('data', {})
        self.assertEqual(data['price'], '')

        new_price = '$1234'
        data['price'] = new_price
        self.assertEqual(data['price'], new_price)

    def test_del_key(self):
        data = AutoCleanRedisDict('data', self._data)
        del data['price']
        self.assertEqual(data['price'], '')

    def test_len(self):
        data = AutoCleanRedisDict('data', self._data)
        self.assertTrue(len(data), len(self._data))

    def test_auto_clean(self):
        data = AutoCleanRedisDict('data', self._data)
        new_price = '$567'
        data2 = AutoCleanRedisDict('data', {'price': new_price})
        self.assertEqual(data['price'], data2['price'])
        self.assertEqual(data2['price'], new_price)

    def test_iter(self):
        data = AutoCleanRedisDict('data', self._data)
        self.assertListEqual(data.keys(), self._data.keys())
        self.assertListEqual(data.values(), self._data.values())

    def test_redis_dict(self):
        RedisDict('data', {}).del_all()

        data = RedisDict('data', self._data)
        self.assertEqual(data['price'], self._data['price'])

        new_price = '$567'
        data2 = RedisDict('data', {'price': new_price})
        self.assertEqual(data['price'], self._data['price'])

        data2['price'] = new_price
        self.assertEqual(data['price'], new_price)

    def test_with_default_dict(self):
        d = collections.defaultdict(lambda: 'a')
        d.update(dict(self._data))

        data = AutoCleanRedisDict('data', d)
        self.assertEqual(data['price'], self._data['price'])
        self.assertEqual(data[str(uuid.uuid4())], 'a')

    def test_type(self):
        with self.assertRaises(ValueError):
            AutoCleanRedisDict('data', {'nums': [1, 2, 3, 4]})

        with self.assertRaises(ValueError):
            AutoCleanRedisDict('data', {'user_data': {}})

