from setuptools import setup, find_packages


setup(
    name='cnaming',
    author='Stefan Hackenberg',
    author_email='mail@stefan-hackenberg.de',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'clang',
    ],
    scripts=[
        'bin/cnaming-check',
    ],
    test_suite='tests',
)
