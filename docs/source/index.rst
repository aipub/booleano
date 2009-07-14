.. _booleano:

Booleano: Boolean Expressions Interpreter
=========================================

:Author: `Gustavo Narea <http://gustavonarea.net/>`_.
:Latest release: |release|
:Date: |today|.

.. topic:: Overview

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


The Three Use Cases
-------------------

Booleano has been designed to address the following use cases:

#. `Convert text-based conditions`_: When you need to turn a condition available
   as plain text into something else (i.e., another filter).
#. `Evaluate text-based conditions`_: When you have a condition available as
   plain text and need to iterate over items in order to filter out those for
   which the evaluation of the condition is not successful.
#. `Evaluate Python-based conditions`_: When you have a condition represented
   by a Python object (nothing to be parsed) and need to iterate over
   items in order to filter out those for which the evaluation of the condition
   is not successful.



Convert text-based conditions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Say you have an online bookstore and you want your book search engine to support
advanced queries that are hard to create with forms. You can have Booleano
convert your users' query expressions into safe SQL *WHERE* clauses.

For example, if an user enters::

    "python" in title and category == "computing" and (rating > 3 or publication_date:year => 2007) and (not software or software:works_on_linux)

Booleano will parse that expression and will use a converter (defined by you)
to turn the resulting :term:`parse tree` into a *WHERE* clause which filters
the books that meet all the requirements below:

* The book title contains the word "python".
* The book falls into the category "computing".
* The book has an average rating of at least 3 **or** it was published after
  2006.
* If the books ships with a software CD, the software must work under Linux.

Of course, Booleano could also handle a simpler expression.

.. note::
    The conversion result doesn't have to be text too, it can be any Python
    object. For example, if you use `SQLAlchemy <http://www.sqlalchemy.org/>`_,
    your converter can turn the parse trees into SQLAlchemy filters.


Evaluate text-based conditions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Say you've created an alternative to the Unix utility `find
<http://en.wikipedia.org/wiki/Find>`_, but unlike :command:`find`, users of your
application don't filter results with `command switches
<http://en.wikipedia.org/wiki/Command-line_argument>`_. Instead, they use
boolean expressions to filter the files/directories.

For example, if an user runs the following command (where "search" is the name
of your application)::

    search / 'file:extension in {"html", "htm", "xhtml"} and ("www-data" in file:owner:groups or users:current_user == file:owner)'

Then, Booleano will parse the expression delimited by single quotes and
:command:`search` will iterate over all the files in the filesystem. On every
iteration, :command:`search` will use the :term:`parse tree` returned by 
Booleano and will evaluate it against the current file; if evaluation fails,
the file is excluded from the results; otherwise, it's included.

With the fictitious command above, only those HTML documents that meet at least
one of the following conditions are included:

* The owner of the file belongs to the "www-data" group (i.e., is a webmaster).
* The owner of the file is the user that is running the command.

Again, Booleano could also handle a simpler expression (such as
``'file:type == mime_types:html'`` just to filter in all the HTML documents).


Evaluate Python-based conditions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Say you're using a third party Web `authorization 
<http://en.wikipedia.org/wiki/Authorization>`_ library which grants access if
and only if the callable you pass to it returns ``True``. On the other hand,
the library provides you with one Booleano variable (which is an stateless
object) called "current_user", that represents the name of the current user (if
he is authenticated).

You could build your Python-based condition like this::

    >>> from authorization_library import current_user
    >>> condition = current_user == "foo"
    >>> condition
    <Equal <Variable "current_user"> <String "foo">>

So ``condition`` represents an stateless object which the authorization
library uses when it needs to find what requests should be allowed or forbidden.
Internally, it executes ``condition`` by passing all the request variables, so
all the operations inside ``condition`` can find if they are met or not.


Features
--------

The general features of Booleano include:

* Supported operands: Strings, numbers, sets, variables and functions.
* Supported operations:

  * Relationals ("equals to", "not equals", "less than", "greater than",
    "less than or equal to" and "greater than or equal to").
  * Membership ("belongs to" and "is subset of").
  * Logical connectives: "not", "and", "xor" and "or".

* Supports Python 2.4 through 2.6.
* Comprehensive unit test suite, which covers the 100% of the package.
* `Freedomware <http://www.softwareliberty.com/>`_, released under the `MIT/X
  License <http://www.opensource.org/licenses/mit-license.php>`_. 

While the parser-specific features include:

* :term:`Binding` support (the operands can be bound to :term:`identifiers
  <identifier>`).
* :term:`Namespace` support (the identifiers may belong to namespaces).
* Boolean expressions can contain any Unicode character. Even identifiers can
  contain non-ASCII characters.
* Localization support. It's easy to have one grammar per supported
  localization.


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

