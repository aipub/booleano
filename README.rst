*****************************************
Booleano: Boolean Expressions Interpreter
*****************************************

:Website: http://code.gustavonarea.net/booleano/

**Booleano** is an interpreter of `boolean expressions
<http://en.wikipedia.org/wiki/Boolean_expression>`_, a library to **define
and run filters** available as text (e.g., in a natural language) or in 
`Python <http://python.org/>`_ code.

In order to handle text-based filters, Booleano ships with a fully-featured
parser whose grammar is :term:`adaptive <adaptive grammar>`. Many
properties can be overridden using simple configuration directives, but
because it's powered by `Pyparsing <http://pyparsing.wikispaces.com/>`_,
you can use it to define complex grammars too.

On the other hand, the library exposes a pythonic API for filters written
in pure Python. These filters are particularly useful to build reusable
conditions from objects provided by a third party library.

