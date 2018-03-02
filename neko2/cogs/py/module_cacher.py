#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Here be dragons.

This deals with inspecting each module given by a module walker, before
outputting any data as a dict.
"""
import inspect
import re
import typing

from . import module_hasher
from . import module_walker


# Takes any permutations of the formats:
# a
# a:b
# a:b = c
# a = c
# and outputs three values: a, b, c
# param_regex = re.compile(r'^(\w+)\s*(?::\s*([^=]+))\s*(?:=\s*(.+))$')
_param_name_re = re.compile(r'^(\w+)')
_param_annotation_re = re.compile(r'.*:\s*(\w+)')
_param_default_re = re.compile(r'.*=\s*(\w+)')

# When we stringify a signature, we get
# <Signature (params here) -> annotation>
# This regex should extract the ``annotation`` part of the string.
_sig_annot_regex = re.compile(r'-> (.+)')


class ModuleCacher:
    def __init__(self, name: str, relative_to: str=None) -> None:
        self._name, self._rel = name, relative_to
        # Maps names to file names
        self._filename_cache = {}

    def _resolve_path(self, name: str, obj):
        """
        Attempts to resolve the closest path to the given object given the
        fully qualified name for it. This will attempt to look in the filename
        cache if need-be. This is because simple object types like integers do
        not retain ownership information in the same way a function would, so
        an integer with fqn ``a.b.c.d`` can be assumed to be in the same file
        as ``a.b.c``, or ``a.b`` or ``a``. Failing this, we give up and return
        None. This is brute force best effort and assumes that the walker
        outputs in a top-down order, otherwise the cache method will never
        actually work.
        """
        try:
            return inspect.getabsfile(obj)
        except:
            pass

        stack = name.split('.')
        while stack:
            stack.pop()
            parent = '.'.join(stack)
            if parent in self._filename_cache:
                return self._filename_cache[parent]

    @staticmethod
    def _qual_name(klass):
        # Gets the qualified name of a class (hopefully)
        if hasattr(klass, '__module__') and klass.__module__:
            return klass.__module__ + '.' + klass.__qualname__
        else:
            return klass.__qualname__

    @staticmethod
    def _get_return_annotation(signature: inspect.Signature):
        # Gets the return type annotation of a signature, if there is one.
        try:
            return _sig_annot_regex.match(str(signature)).group(1)
        except:
            return None

    @staticmethod
    def _get_param_meta(parameter: inspect.Parameter):
        # Returns a dict of attributes about a parameter
        p_str = str(parameter)

        annotation = _param_annotation_re.match(p_str)
        annotation = annotation.group(1) if annotation else None
        default = _param_default_re.match(p_str)
        default = default.group(1) if default else None

        result = {
            'name': parameter.name,
            'annotation': annotation,
            'default': default,
            # Type: _ParameterKind enum -> str
            'kind': parameter.kind.name.replace('_', ' ').title()
        }

        return result

    def make_cache(self) -> typing.Dict[str, typing.Any]:
        """
        Creates a cache dict and returns it.
        """
        walker = module_walker.ModuleWalker(self._name, self._rel)
        module_hash = str(module_hasher.get_module_hash(walker.start))
        attrs = [attr for attr in walker]

        # Holds our metadata.
        attr_meta = {}

        data = {
            "hash": module_hash,
            'hashing_algorithm': module_hasher.hash_alg,
            "root": walker.start.__name__,
            "attrs": attr_meta
        }

        for apparent_name, real_name, obj in attrs:
            parent, _, name = apparent_name.rpartition('.')

            try:
                file = self._resolve_path(real_name, obj)
                file = file[file.find(walker.start.__name__):]
            except:
                file = None

            if file:
                self._filename_cache[apparent_name] = file
                self._filename_cache[real_name] = file

            docstring = inspect.getdoc(obj)
            if docstring:
                docstring = inspect.cleandoc(docstring)

            try:
                lines = inspect.getsourcelines(obj)
                start_line = lines[1] + 1
                end_line = start_line + len(lines[0])
            except:
                start_line = 1
                end_line = 1

            # Data that is stored in an attr no matter the type.
            attr = {
                'category': None,
                'name': name,
                'parent': parent,
                'fqn': apparent_name,
                'actual_fqn': real_name,
                'file': file,
                'docstring': docstring,
                'start_line': start_line,
                'end_line': end_line
            }

            if inspect.ismodule(obj):
                attr['category'] = 'module'
            elif inspect.isclass(obj):
                attr['category'] = 'class'

                obj: type
                attr['bases'] = [self._qual_name(b) for b in obj.__bases__]

                class_attrs = {}

                for attr_name, kind, _, _ in inspect.classify_class_attrs(obj):
                    if not attr_name.startswith('__'):
                        class_attrs[attr_name] = kind

                attr['attrs'] = class_attrs

                pass
            elif inspect.isfunction(obj):
                attr['category'] = 'function'
                s = inspect.signature(obj)
                attr['return_hint'] = self._get_return_annotation(s)
                attr['params'] = [self._get_param_meta(p)
                                  for p in s.parameters.values()]
            else:
                # General attribute.
                attr['category'] = 'attribute'

            attr_meta[apparent_name] = attr

        return data


