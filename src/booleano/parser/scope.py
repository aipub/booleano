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

from booleano.exc import ScopeError


__all__ = ("Bind", "Namespace", "SymbolTable")


class Identifier(object):
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
    
    def get_contents(self):
        raise NotImplemented()
    
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
        if (isinstance(other, Identifier) and
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


class Bind(Identifier):
    """
    Operand binding.
    
    """
    
    def __init__(self, global_name, operand, **names):
        self.operand = operand
        super(Bind, self).__init__(global_name, **names)
    
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


class Namespace(Identifier):
    """
    Booleano namespace.
    
    Namespaces wrap *bound* operands (aka, "bindings").
    
    """
    
    def __init__(self, global_name, objects, namespaces=[], **names):
        """
        Create a new namespace called ``global_name``.
        
        :param global_name: The name of namespace (excludes parent namespaces,
            if any).
        :type global_name: basestring
        :param objects: List of bound operands available in this namespace.
        :type objects: list
        :param namespaces: List of sub-namespaces.
        :type namespaces: list
        
        Additional keyword arguments represent the other names this namespace
        can take in different locales.
        
        """
        super(Namespace, self).__init__(global_name, **names)
        self.objects = set()
        self.subnamespaces = set()
        for obj in objects:
            self.add_object(obj)
        for ns in namespaces:
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
                if locale in obj.names:
                    name = obj.names[locale]
                else:
                    name = obj.global_name
                if name in used_object_names:
                    raise ScopeError('The name "%s" is shared by two or more '
                                     'bindings in %s (locale: %s)' %
                                     (name, self, locale))
                used_object_names.add(name)
            
            # Checking the subnamespaces:
            used_ns_names = set()
            for ns in self.subnamespaces:
                if locale in ns.names:
                    name = ns.names[locale]
                else:
                    name = ns.global_name
                if name in used_ns_names:
                    raise ScopeError('The name "%s" is shared by two or more '
                                     'sub-namespaces in %s (locale: %s)' %
                                     (name, self, locale))
                used_ns_names.add(name)
    
    def get_symbol_table(self, locale=None):
        objects = self._extract_items(self.objects, locale)
        subtables = self._extract_items(self.subnamespaces, locale)
        
        return SymbolTable(objects, subtables)
    
    def _extract_items(self, items, extractor, locale=None):
        extracted_items = {}
        
        if locale:
            for item in items:
                if locale in item.names:
                    localized_name = item.names[locale]
                else:
                    # TODO: Raise warning
                    localized_name = obj.global_name
                unbindings[localized_name] = extractor(item, locale)
        else:
            for item in items:
                unbindings[obj.global_name] = extractor(item, locale)
        
        if len(extracted_items) != len(items):
            if locale:
                msg = u"Two namespaces or bound operands share the same " \
                       "name in the locale %s at %s" % (locale, self)
            else:
                msg = u"Two namespaces or bound operands share the same " \
                       "global name at %s" % self
            raise ScopeError(msg)
        
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
        (:meth:`Identifier.__eq__`) and wrap the same objects and subnamespaces.
        
        """
        same_id = super(Namespace, self).__eq__(other)
        return (same_id and 
                hasattr(other, "subnamespaces") and 
                hasattr(other, "objects") and 
                other.subnamespaces == self.subnamespaces and
                self.objects == other.objects)


class SymbolTable(object):
    """
    A symbol table for a given locale.
    
    This is not aimed at end-users, it should only be used internally in
    Booleano.
    
    The parser only deals with this, not with the namespaces directly.
    
    A namespace has one symbol table per locale.
    
    """
    
    def __init__(self, global_objects, subtables):
        self.global_objects = global_objects
        self.subtables = subtables
    
    def get_object(self, object_name, namespace=None):
        """
        Return the object identified by ``object_name``, which is under the
        namespace ``namespace``.
        
        :param object_name: The name of the object to be returned.
        :type object_name: basestring
        :param namespace: The namespace under which the object is or ``None``
            if it's in the global namespace.
        :type namespace: tuple
        :return: The requested object.
        :rtype: Operand
        
        """
        raise NotImplementedError
    
    def get_child(self, namespace):
        namespace_aux = self.namespaces
        for name in namespace:
            namespace_aux = namespace_aux[name]
        return namespace_aux

