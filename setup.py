from setuptools import setup


setup(
    name='cnaming',
    author='Stefan Hackenberg',
    author_email='mail@stefan-hackenberg.de',
    version='0.1',
    packages=['cnaming'],
    install_requires=[
        'clang',
    ],
    scripts=[
        'bin/cnaming-check',
    ],
    tests=['tests'],
)
