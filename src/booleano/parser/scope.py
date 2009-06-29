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
"""
Booleano scope handling.

"""

from logging import getLogger

from booleano.exc import ScopeError


__all__ = ("Bind", "Namespace", "SymbolTable")


LOGGER = getLogger(__name__)


class _Identifier(object):
    """
    Multilingual identifier.
    
    """
    
    def __init__(self, global_name, **names):
        """
        Create the identifier using ``global_name`` as it's name.
        
        :param global_name: The name of namespace (excludes parent namespaces,
            if any).
        :type global_name: basestring
        
        Additional keyword arguments represent the other names this namespace
        can take in different languages.
        
        """
        self.namespace = None
        self.global_name = global_name.lower()
        # Convert the ``names`` to lower-case:
        for (locale, name) in names.items():
            names[locale] = name.lower()
        self.names = names
    
    def get_localized_name(self, locale):
        """
        Return the localized name of the identifier in ``locale``.
        
        :param locale: The locale of the name.
        :type locale: basestring
        :return: The name of the identifier in ``locale``; if it's not defined,
            the global name is returned.
        :rtype: basestring
        
        """
        if locale in self.names:
            name = self.names[locale]
        else:
            LOGGER.warn("%s doesn't have a name in %s; using the global one",
                        self, locale)
            name = self.global_name
        return name
    
    def _get_contents(self, locale):
        """
        Return the contents being wrapped, filtered by ``locale`` where
        relevant.
        
        :param locale: The locale used to filter the contents.
        :param locale: basestring
        :return: The contents being wrapped; in a binding, it's the operand,
            while in a namespace, it's the symbol table for the ``locale``.
        
        """
        raise NotImplementedError()
    
    #{ Comparison stuff
    
    def __hash__(self):
        """
        Make the identifier hashable based on its global name.
        
        """
        first = ord(self.global_name[0])
        last = ord(self.global_name[-1])
        hash_ = first*2 + last*3 + len(self.global_name)
        return hash_
    
    def __eq__(self, other):
        """
        Check that the ``other`` identifier is equivalent to this one.
        
        Two identifiers are equivalent if the have the same names.
        
        """
        if (isinstance(other, _Identifier) and
            self.global_name == other.global_name and
            self.names == other.names):
            return True
        return False
    
    def __ne__(self, other):
        """
        Check that the ``other`` identifier is NOT equivalent to this one.
        
        """
        return not self.__eq__(other)
    
    #{ Representations
    
    def __unicode__(self):
        """
        Return the Unicode representation for the identifier.
        
        This must be overridden by the specific identifiers.
        
        """
        raise NotImplementedError("Identifiers must set their Unicode "
                                  "representation")
    
    def __str__(self):
        """
        Return the ASCII representation for this identifier.
        
        This method returns the same as :meth:`__unicode__`.
        
        """
        return self.__unicode__().encode("utf-8")
    
    #}


class Bind(_Identifier):
    """
    Operand binding.
    
    """
    
    def __init__(self, global_name, operand, **names):
        self.operand = operand
        super(Bind, self).__init__(global_name, **names)
    
    def _get_contents(self, locale):
        """
        Return the operand bound.
        
        The ``locale`` does nothing here.
        
        """
        return self.operand
    
    def __eq__(self, other):
        """
        Check that the ``other`` binding is equivalent to this one.
        
        Two bindings are equivalent if they have the same names, even though
        they don't wrap the same operand.
        
        """
        same_id = super(Bind, self).__eq__(other)
        # We have to make sure ``other`` is a binding; otherwise, a namespace
        # with the same names would equal this binding:
        return (same_id and isinstance(other, Bind))
    
    def __unicode__(self):
        """
        Return the Unicode representation for this binding, including its
        namespace.
        
        """
        description = u'Operand %s bound as "%s"' % (self.operand,
                                                     self.global_name)
        if self.namespace:
            description = "%s (at %s)" % (description, self.namespace)
        return description


class Namespace(_Identifier):
    """
    Booleano namespace.
    
    Namespaces wrap *bound* operands (aka, "bindings").
    
    """
    
    def __init__(self, global_name, objects, *subnamespaces, **names):
        """
        Create a new namespace called ``global_name``.
        
        :param global_name: The name of namespace (excludes parent namespaces,
            if any).
        :type global_name: basestring
        :param objects: List of bound operands available in this namespace.
        :type objects: list
        
        Additional positional arguments represent the sub-namespaces of this
        namespace.
        
        Additional keyword arguments represent the other names this namespace
        can take in different locales.
        
        """
        super(Namespace, self).__init__(global_name, **names)
        self.objects = set()
        self.subnamespaces = set()
        for obj in objects:
            self.add_object(obj)
        for ns in subnamespaces:
            self.add_namespace(ns)
    
    def add_object(self, obj):
        """
        Add the ``obj`` object to this namespace.
        
        :param obj: The bound operand to be added.
        :type obj: Bind
        :raises ScopeError: If ``obj`` is already included or it already
            belongs to another namespace.
        
        """
        # Checking if it's safe to include the object:
        if obj.namespace:
            raise ScopeError(u"%s already belongs to %s" % (obj.global_name,
                                                            obj.namespace))
        if obj in self.objects or obj.namespace:
            raise ScopeError(u"An equivalent of %s is already defined in %s" %
                             (obj, self))
        
        # It's safe to include it!
        obj.namespace = self
        self.objects.add(obj)
    
    def add_namespace(self, subnamespace):
        """
        Add the ``subnamespace`` namespace to this namespace.
        
        :param subnamespace: The namespace to be added.
        :type subnamespace: Namespace
        :raises ScopeError: If ``subnamespace`` is already included or it
            already belongs to another namespace.
        
        """
        # Checking if it's safe to include the sub-namespace:
        if subnamespace.namespace:
            raise ScopeError(u"%s already belongs to %s" %
                             (subnamespace, subnamespace.namespace))
        if subnamespace in self.subnamespaces:
            raise ScopeError(u"An equivalent of %s is already available in %s" %
                             (subnamespace, self))
        
        # It's safe to include it!
        subnamespace.namespace = self
        self.subnamespaces.add(subnamespace)
    
    def validate_scope(self):
        """
        Make sure there's no name clash in the namespace.
        
        :raise ScopeError: If a name clash in found, either in the global names
            or with the localized names.
        
        Users may want to run this in their test suite, instead of in
        production, for performance reasons.
        
        Note that it's perfectly valid for one object and one subnamespace to
        have the same name in the parent namespace.
        
        """
        # <--- Checking that there's no name clash among the global names
        
        unique_objects = set([obj.global_name for obj in self.objects])
        if len(unique_objects) != len(self.objects):
            raise ScopeError("Two or more objects in %s share the same global "
                             "name" % self)
        
        unique_namespaces = set([ns.global_name for ns in self.subnamespaces])
        if len(unique_namespaces) != len(self.subnamespaces):
            raise ScopeError("Two or more subnamespaces in %s share the same "
                             "global name" % self)
        
        # <--- Checking that there's no name clash in the sub-namespaces
        for ns in self.subnamespaces:
            ns.validate_scope()
        
        # <--- Checking that there's no name clash among the localized names
        
        # Collecting all the locales used:
        locales = set()
        for id_ in (self.objects | self.subnamespaces):
            locales |= set(id_.names.keys())
        
        # Now let's see if any of them are duplicate:
        for locale in locales:
            # Checking the objects:
            used_object_names = set()
            for obj in self.objects:
                name = obj.get_localized_name(locale)
                if name in used_object_names:
                    raise ScopeError('The name "%s" is shared by two or more '
                                     'bindings in %s (locale: %s)' %
                                     (name, self, locale))
                used_object_names.add(name)
            
            # Checking the subnamespaces:
            used_ns_names = set()
            for ns in self.subnamespaces:
                name = ns.get_localized_name(locale)
                if name in used_ns_names:
                    raise ScopeError('The name "%s" is shared by two or more '
                                     'sub-namespaces in %s (locale: %s)' %
                                     (name, self, locale))
                used_ns_names.add(name)
    
    def get_symbol_table(self, locale=None):
        """
        Return the symbol table for this namespace in the ``locale``.
        
        :param locale: The locale of the symbol table; if ``None``, the global
            names will be used instead.
        :param locale: basestring
        :return: The symbol table in ``locale``.
        :rtype: SymbolTable
        
        """
        objects = self._get_objects(locale)
        subtables = self._get_subtables(locale)
        return SymbolTable(objects, subtables)
    
    def __unicode__(self):
        """
        Return the Unicode representation for this namespace, including its
        ancestors.
        
        """
        ancestors = self._get_ancestors_global_names()
        names = u":".join(ancestors)
        return u"Namespace %s" % names
    
    def __eq__(self, other):
        """
        Check that the ``other`` namespace is equivalent to this one.
        
        Two namespaces are equivalent if they are equivalent identifiers
        (:meth:`_Identifier.__eq__`) and wrap the same objects and
        subnamespaces.
        
        """
        same_id = super(Namespace, self).__eq__(other)
        return (same_id and 
                hasattr(other, "subnamespaces") and 
                hasattr(other, "objects") and 
                other.subnamespaces == self.subnamespaces and
                self.objects == other.objects)
    
    def _get_contents(self, locale):
        """Return the symbol table for this namespace in ``locale``."""
        return self.get_symbol_table(locale)
    
    def _get_objects(self, locale):
        """
        Return the objects available in this namespace.
        
        :param locale: The locale to be used while resolving the names of the
            objects.
        :type locale: basestring
        :return: The operands in this namespace, in a dictionary whose keys
            are the names of the objects in ``locale``.
        :rtype: dict
        
        """
        objects = self.__extract_items__(self.objects, locale)
        return objects
    
    def _get_subtables(self, locale):
        """
        Return the sub-namespaces available under this namespace turned into
        symbol tables for the ``locale``.
        
        :param locale: The locale to be used while resolving the names of the
            sub-namespaces.
        :type locale: basestring
        :return: The symbol tables for the sub-namespaces under this namespace,
            in a dictionary whose keys are the names of the tables in
            ``locale``.
        :rtype: dict
        
        """
        subtables = self.__extract_items__(self.subnamespaces, locale)
        return subtables
    
    def __extract_items__(self, items, locale):
        """
        Filter the contents of the ``items`` identifiers based on the
        ``locale``.
        
        :param items: A list of identifiers whose contents should be extracted.
        :type items: list
        :param locale: The locale to be used to filter the contents.
        :type locale: basestring or ``None``
        :return: The contents of each item in ``items``, in a dictionary whose
            keys are the names of such items in the ``locale``.
        :rtype: dict
        
        """
        extracted_items = {}
        
        if locale:
            # The items have to be extracted by their localized names:
            for item in items:
                localized_name = item.get_localized_name(locale)
                extracted_items[localized_name] = item._get_contents(locale)
        else:
            # We have to extract the items by their global names:
            for item in items:
                extracted_items[item.global_name] = item._get_contents(locale)
        
        return extracted_items
    
    def _get_ancestors_global_names(self):
        """
        Return the global names for the ancestors **and** the current namespace.
        
        :return: The list of names, from the topmost namespace to the current
            one.
        :rtype: list
        
        """
        if self.namespace:
            ancestors = self.namespace._get_ancestors_global_names()
        else:
            ancestors = []
        ancestors.append(self.global_name)
        return ancestors


class SymbolTable(object):
    """
    A symbol table for a given locale.
    
    This is not aimed at end-users, it should only be used internally in
    Booleano.
    
    The parser only deals with this, not with the namespaces directly.
    
    A namespace has one symbol table per locale.
    
    """
    
    def __init__(self, objects, subtables={}):
        """
        Create a symbol table made up of ``objects``.
        
        :param objects: The objects that belong to the table.
        :type objects: dict
        :param subtables: The symbol tables under this table, if any.
        :type subtables: dict
        
        """
        self.objects = objects
        self.subtables = subtables
    
    def get_object(self, object_name, subtable_parts=None):
        """
        Return the object identified by ``object_name``, which is under the
        symbol table whose names are ``subtable_parts``.
        
        :param object_name: The name of the object to be returned.
        :type object_name: basestring
        :param subtable_parts: The symbol table that contains the object
            identified by ``object_name``, represented by a list of names.
        :type subtable_parts: list
        :return: The requested object.
        :rtype: Operand
        :raises ScopeError: If the requested object doesn't exist in the
            symbol table, or if the symbol table doesn't exist.
        
        """
        table = self._get_subtable(subtable_parts)
        if table is None or object_name not in table.objects:
            msg = u'No such object "%s"' % object_name
            if subtable_parts:
                msg = u'%s in %s' % (msg, u":".join(subtable_parts))
            raise ScopeError(msg)
        return table.objects[object_name]
    
    def _get_subtable(self, subtable_parts):
        """
        Return the subtable represented by the names in ``subtable_parts``.
        
        :param subtable_parts: The names that resolve a subtable in this
            table.
        :type subtable_parts: list
        :return: The symbol table represented by the names in 
            ``subtable_parts`` or ``None`` if it's not found.
        :rtype: SymbolTable
        
        """
        if not subtable_parts:
            return self
        current_part = subtable_parts.pop(0)
        if current_part not in self.subtables:
            return None
        return self.subtables[current_part]._get_subtable(subtable_parts)

