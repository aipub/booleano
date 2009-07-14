.. _booleano:

Booleano: Boolean Expressions Interpreter
=========================================

:Author: `Gustavo Narea <http://gustavonarea.net/>`_.
:Date: |today|.

.. topic:: Overview

    **Booleano** is a `free <http://www.softwareliberty.com/>`_ 
    `pythonic <http://python.org/>`_ interpreter of 
    `boolean expressions <http://en.wikipedia.org/wiki/Boolean_expression>`_,
    a library to **define and run filters** written in a natural language or
    with pure Python code.
    
    In order to handle filters written in natural languages, Booleano ships
    with a fully-featured parser whose grammar is adaptive (i.e., you'll be
    able to customize most of the properties in the language being used). Many
    properties can be overridden using simple configuration directives,
    but because it's powered by `Pyparsing <http://pyparsing.wikispaces.com/>`_
    under-the-hood, you can use it to define complex grammars too.
    
    On the other hand, the library exposes a pythonic API for filters written
    in pure Python. These filters are particularly useful to build reusable
    conditions from objects provided by a third party library.

Features
--------

Booleano supports literals (strings, numbers and sets), identifiers 
(variables and functions), namespaces, relational operations ("equals",
"not equals", "less than", "greater than", "less than or equal to" and
"greater than or equal to"), membership operations ("belongs to" and
"is subset of") and, of course, logical connectives ("not", "and", "xor" and
"or").

Because of the above, it is very likely that Booleano will suit at least the

The Three Use Cases
-------------------

Booleano has been designed to address three use cases:


Contents
--------

.. toctree::
   :maxdepth: 2
   
   tutorials/index
   manual/index
   api/index
   about
   changes


Indices and tables
^^^^^^^^^^^^^^^^^^

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

