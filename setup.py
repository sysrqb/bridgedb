#!/usr/bin/python
# BridgeDB by Nick Mathewson.
# Copyright (c) 2007-2009, The Tor Project, Inc.
# See LICENSE for licensing information

import distutils
import subprocess
from distutils.command.install_data import install_data as _install_data
import os
import sys
from setuptools import setup, Command, find_packages

# Fix circular dependency with setup.py install
try:
    from babel.messages.frontend import compile_catalog, extract_messages
    from babel.messages.frontend import init_catalog, update_catalog
except ImportError:
    compile_catalog = extract_messages = init_catalog = update_catalog = None

class installData(_install_data):
    def run(self):
        self.data_files = []
        for lang in os.listdir('build/locale/'):
            if lang.endswith('templates'):
                continue
            lang_dir = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
            lang_file = os.path.join('build', 'locale', lang, 'LC_MESSAGES', 
                                     'bridgedb.mo')
            self.data_files.append( (lang_dir, [lang_file]) )
        _install_data.run(self)

class runTests(Command):
    # Based on setup.py from mixminion, which is based on setup.py
    # from Zooko's pyutil package, which is in turn based on
    # http://mail.python.org/pipermail/distutils-sig/2002-January/002714.html
    description = "Run unit tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        build = self.get_finalized_command('build')
        self.build_purelib = build.build_purelib
        self.build_platlib = build.build_platlib

    def run(self):
        self.run_command('build')
        old_path = sys.path[:]
        sys.path[0:0] = [ self.build_purelib, self.build_platlib ]
        try:
            testmod = __import__("bridgedb.Tests", globals(), "", [])
            testmod.Tests.main()
        finally:
            sys.path = old_path

setup(name='BridgeDB',
      version='0.1',
      description='Bridge disbursal tool for use with Tor anonymity network',
      author='Nick Mathewson',
      author_email='nickm at torproject dot org',
      url='https://www.torproject.org',
      package_dir= {'' : 'lib'},
      packages=find_packages('lib'),
      py_modules=['TorBridgeDB'],
      cmdclass={'test' : runTests,
                'compile_catalog': compile_catalog,
                'extract_messages': extract_messages,
                'init_catalog': init_catalog,
                'update_catalog': update_catalog,
                'install_data': installData},
      include_package_data=True,
      package_data={'bridgedb': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*.html',
                                 'templates/assets/*']},
      message_extractors = {'lib/bridgedb': [
              ('**.py', 'python', None),
              ('templates/**.html', 'mako', None),
              ('public/**', 'ignore', None)]},  
)
