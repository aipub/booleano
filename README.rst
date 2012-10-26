Booleano: Boolean Expressions Interpreter
=========================================

**Booleano** is an interpreter of `boolean expressions
<http://en.wikipedia.org/wiki/Boolean_expression>`_, a library to **define
and run filters** available as text (e.g., in a natural language) or in
`Python <http://python.org/>`_ code.

In order to handle text-based filters, Booleano ships with a fully-featured
parser whose grammar is `adaptive
<http://en.wikipedia.org/wiki/Adaptive_grammar>`_: Its properties
can be overridden using simple configuration directives.

On the other hand, the library exposes a pythonic API for filters written
in pure Python. These filters are particularly useful to build reusable
conditions from objects provided by a third party library.

This is fork of `https://code.launchpad.net/booleano`
Code im main branch does not work, so i create my branch from 1.0a1 version, that is usable.
Date parsing example for pyparsing taken from `http://pcscholl.de/2009/09/24/better-later-than-never-the-pyparsing-based-date-parser/`
Default locale is en_US, you must specify locale when calling ParseManager.parse method.
Months long and short names are from PyICU, which is dependency now.

Links
-----

* `Web site <http://code.gustavonarea.net/booleano/>`_.
* `Mailing list <http://groups.google.com/group/booleano>`_.
* `Bug reports <https://bugs.launchpad.net/booleano>`_.
