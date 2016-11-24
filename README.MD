# RedisDict

A dict-like object using Redis as the backend.


## Example

```
>>> from redisdict import RedisDict
>>> d = RedisDict('d', {})
>>> d['name'] = 'Kxrr'
>>> d['name']
'Kxrr'
```


## TODO

- Complex object supporting