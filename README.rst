Evaluation of boolean expressions in natural languages
======================================================

TODO: Complete this document.

Supported grammar
-----------------

The following Backus-Naur Form (BNF) defines the supported grammar::

    <boolean-expression> ::= <operations>
    
    <operation> ::= 
    
    <flat-operation> ::= <or-operation>*
    <or-operation> ::= <and-operation> ["OR" <and-operation>]
    <and-operation> ::= <basic-operation> ["AND" <basic-operation>]
    
    <basic-operation> ::= ["NOT"] <atom-operand>
    <atom-operand> ::= <number> | <quoted-string> | <variable>
    
    <number> ::= <digit>+ [<decimal-separator> <digit>+]
    <digit> ::= "0".."9"
    <decimal-separator> ::= "."                                   -- replaceable
    <variable> ::= <word> ["." <word>]

Where the following constants can be translated:

- ``"NOT"``.
- ``"."``.
