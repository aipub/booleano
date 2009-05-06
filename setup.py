# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 by Gustavo Narea <http://gustavonarea.net/>
#
# This file is part of Booleano <http://code.gustavonarea.net/booleano/>
#
# Booleano is freedomware: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# Booleano is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Booleano. If not, see <http://www.gnu.org/licenses/>.

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
version = open(os.path.join(here, 'VERSION.txt')).readline().rstrip()

setup(name='booleano',
      version=version,
      description=('Evaluation of boolean expressions in natural languages'),
      long_description=README,
      classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing :: Linguistic",
        ],
      keywords='boolean expression natural language condition',
      author="Gustavo Narea",
      author_email="me@gustavonarea.net",
      url="http://code.gustavonarea.net/booleano/",
      license="GNU General Public License v3 (http://www.gnu.org/copyleft/gpl.html)",
      packages=find_packages('src', exclude=['tests']),
      package_dir={'': 'src'},
      package_data={
        '': ['VERSION.txt', 'README.rst'],
        'docs': ['Makefile', 'conf.py', '**.rst', '_templates/*', '_static/*']},
      exclude_package_data={'': ['README.txt', 'docs']},
      include_package_data=True,
      zip_safe=False,
      tests_require = ['coverage', 'nose'],
      install_requires=['pyparsing >= 1.5.2'],
      test_suite="nose.collector",
      entry_points = """\
      """
      )

