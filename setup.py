# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://booleano.efous.org/>.
#
# This program is Freedomware: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
VERSION = open(os.path.join(HERE, "VERSION.txt")).readline().rstrip()
README = open(os.path.join(HERE, "README.rst")).read()

setup(name="booleano",
      version=VERSION,
      description="Boolean Expressions Interpreter",
      long_description=README,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing :: Linguistic",
        ],
      keywords="boolean expression natural language condition conditions",
      author="Gustavo Narea",
      author_email="me@gustavonarea.net",
      url="http://booleano.efous.org/",
      download_url="https://launchpad.net/booleano/+download",
      license="GNU GPL v3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)",
      namespace_packages = ["booleano"],
      package_dir={'': "src"},
      packages=find_packages("src"),
      zip_safe=False,
      tests_require = ["coverage >= 3.0", "nose >= 0.11.0"],
      install_requires=["pyparsing >= 1.5.2, < 2.0"],
      test_suite="nose.collector",
      )

