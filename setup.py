# -*- coding: utf-8 -*-
#
# Copyright (c) 2009 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://code.gustavonarea.net/booleano/>.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, distribute with
# modifications, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ABOVE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written authorization.

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
        "License :: OSI Approved :: MIT License",
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
      license="MIT X License (http://www.opensource.org/licenses/mit-license.php)",
      namespace_packages = ["booleano"],
      packages=find_packages('src', exclude=['tests']),
      package_dir={'': 'src'},
      package_data={
        '': ['VERSION.txt', 'README.rst'],
        'docs': ['Makefile', 'conf.py', '**.rst', '_templates/*', '_static/*']},
      exclude_package_data={'': ['README.txt', 'docs']},
      include_package_data=True,
      zip_safe=False,
      tests_require = ['coverage', 'nose >= 0.11.0'],
      install_requires=['pyparsing >= 1.5.2'],
      test_suite="nose.collector",
      entry_points = """\
      """
      )

