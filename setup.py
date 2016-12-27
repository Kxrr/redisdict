import setuptools
import codecs


def get_requirements(filename):
    return codecs.open('requirements/' + filename, encoding='utf-8').read().splitlines()


setuptools.setup(
    name='redisdict',
    version='0.0.2',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    url='https://github.com/kxrr/redisdict',
    license='MIT',
    author='kxrr',
    author_email='hi@kxrr.us',
    description='A dict-like object using Redis as the backend.',
    install_requires=get_requirements('default.txt'),
    tests_require=get_requirements('test.txt'),
)
