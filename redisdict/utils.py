# -*- coding: utf-8 -*-
import redis
import uuid
import urlparse
from contextlib import contextmanager

from .exceptions import MutexHeldError


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


@contextmanager
def mutex(client, name, expire):
    """
    :type client: redis.Redis
    """
    lock_id = str(uuid.uuid4())
    won = client.setnx(name, lock_id)
    if won:
        client.expire(name, expire)
        yield
        with client.pipeline(True) as pipe:
            try:
                pipe.watch(name)
                if pipe.get(name) == lock_id:
                    pipe.multi()
                    pipe.delete(name)
                    pipe.execute()
                pipe.unwatch()
            except redis.WatchError:
                pass
    else:
        raise MutexHeldError
