#!/usr/bin/env python

from distutils.core import setup

setup(name='ogame',
      version='1.2.7',
      description='OGame wrapper.',
      author='tw88',
      author_email='ibot.root@gmail.com',
      packages=['ogame'],
      url='https://github.com/tw88/pyogame',
      install_requires=['requests',
                        'arrow',
                        'beautifulsoup4'],
      )
