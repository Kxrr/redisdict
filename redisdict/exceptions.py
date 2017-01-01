#!/usr/bin/env python
# encoding: utf-8


class SerialisationError(TypeError):
    """ Raises when value of dict can't be serialized. """
    pass


class MutexHeldError(RuntimeError):
    pass


class ConfigurationError(Exception):
    pass
