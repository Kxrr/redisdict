import os
import re
import sys
import setuptools
import codecs

if sys.version_info.major > 2:
    raise Exception('Requires python2.')

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'redisdict', '__init__.py')) as f:
    meta_content = f.read()


def get_version():
    pattern = re.compile('^VERSION\s*=\s*\((.*)\)', flags=re.M)
    _version = pattern.search(meta_content).group(1)
    return '.'.join(re.split(',\s*', _version))


def get_requirements(filename):
    return codecs.open('requirements/' + filename, encoding='utf-8').read().splitlines()


setuptools.setup(
    name='redisdict',
    version=get_version(),
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    url='https://github.com/kxrr/redisdict',
    license='MIT',
    author='kxrr',
    author_email='hi@kxrr.us',
    description='A dict-like object using Redis as the backend.',
    install_requires=get_requirements('default.txt'),
    tests_require=get_requirements('test.txt'),
)
