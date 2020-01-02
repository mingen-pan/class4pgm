import io

from setuptools import setup, find_packages


def read_all(f):
    with io.open(f, encoding="utf-8") as file:
        return file.read()


setup(
    name='class4pgm',
    version='0.0.1',
    description='Class Manager for Graph Database',
    long_description=read_all("README.md"),
    long_description_content_type='text/markdown',
    url='https://github.com/mingen-pan/class4pgm/',
    packages=find_packages(),
    install_requires=['redis', 'py2neo', 'redisgraph'],
    classifiers=[
        'Development Status :: Dev',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Database'
    ],
    keywords='Property Graph Database',
    author='Mingen Pan',
    author_email='mepan94@gmail.com'
)
