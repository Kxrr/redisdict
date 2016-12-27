# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
logging.basicConfig()

VERSION = (0, 0, 2)
__version__ = '.'.join(map(str, VERSION))

logger = logging.getLogger('redisdict')

from .redisdict import RedisDict, SimpleRedisDict, ComplexRedisDict
