#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Here be dragons.

This deals with inspecting each module given by a module walker, before
outputting any data as a dict.
"""
import asyncio                 # Gather
import enum                    # Enum
import inspect                 # Inspection utils
import re                      # Regex
import traceback               # Exception utilities
import typing                  # Type checking and annotation fetching
import bs4                     # HTML parser
from docutils import frontend  # Docutils frontend (config proxy)
from docutils import utils     # document type
from sphinx import parsers     # ReStructured Text Parser
from . import module_hasher    # Module hashing
from . import module_walker    # Module member recursive walker

# Set to True to fill your system journal quickly ;)
DEBUG = False


def trace():
    if DEBUG:
        traceback.print_exc()


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

# Maps common magic methods to their respective operator or call.
operators = {
    '__abs__': 'abs()',
    '__add__': '+',
    '__aenter__': 'async with self',
    '__aiter__': 'in (async iterator)',
    '__and__': '&',
    '__anext__': 'await next()',
    '__await__': 'await self',
    '__bool__': 'bool()',
    '__bytes__': 'bytes()',
    '__call__': 'self()',
    '__complex__': 'complex()',
    '__contains__': 'in (contains)',
    '__del__': 'del self',
    '__delattr__': 'delattr()',
    '__delitem__': 'del []',
    '__dir__': 'dir()',
    '__divmod__': 'divmod()',
    '__enter__': 'with self',
    '__eq__': '==',
    '__float__': 'float()',
    '__floordiv__': '//',
    '__format__': 'format()',
    '__ge__': '>=',
    '__getattr__': 'getattr()',
    '__getitem__': '_ = []',
    '__gt__': '>',
    '__hash__': 'hash()',
    '__iadd__': '+',
    '__iand__': '&',
    '__idivmod__': 'divmod()',
    '__ifloordiv__': '//',
    '__ilshift__': '<<',
    '__imatmul__': '@',
    '__imod__': '%',
    '__imul__': '*',
    '__index__': 'operators.index()',
    '__int__': 'int()',
    '__invert__': '~self',
    '__ior__': '|',
    '__ipow__': '**',
    '__irshift__': '>>',
    '__isub__': '-',
    '__iter__': 'in (iterator)',
    '__itruediv__': '/',
    '__ixor__': '^',
    '__le__': '<=',
    '__len__': 'len()',
    '__length_hint__': 'operator.length_hint()',
    '__lshift__': '<<',
    '__lt__': '<',
    '__matmul__': '@',
    '__mod__': '%',
    '__mul__': '*',
    '__ne__': '!=',
    '__neg__': '-self',
    '__next__': 'next()',
    '__or__': '|',
    '__pos__': '+self',
    '__pow__': '**',
    '__radd__': '+',
    '__rand__': '&',
    '__rdivmod__': 'divmod()',
    '__repr__': 'repr()',
    '__reversed__': 'reversed()',
    '__rfloordiv__': '//',
    '__rlshift__': '<<',
    '__rmatmul__': '@',
    '__rmod__': '%',
    '__rmul__': '*',
    '__ror__': '|',
    '__round__': 'round()',
    '__rpow__': '**',
    '__rrshift__': '>>',
    '__rshift__': '>>',
    '__rsub__': '-',
    '__rtruediv__': '/',
    '__rxor__': '^',
    '__setattr__': 'setattr()',
    '__setitem__': '[] = _',
    '__str__': 'str()',
    '__sub__': '-',
    '__truediv__': '/',
    '__xor__': '^',
}


def _get_operators(obj):
    impl_ops = set()
    impl_dir = dir(obj)

    for operator in operators:
        if operator in impl_dir:
            impl_ops.add(operators[operator])

    return list(sorted(impl_ops))


class ModuleCacher:
    def __init__(self, name: str, relative_to: str = None) -> None:
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
            trace()
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
    def _parse_docstring(docstring):
        #  Get a DOM
        # doctree = publish_doctree(docstring).asdom()
        #  Get an element tree (meant to be simpler to use)
        parser = parsers.RSTParser(rfc2822=False)
        settings = frontend.OptionParser(
            components=(parsers.RSTParser,),
            # Apparently 5 means quiet?
            defaults={'report_level': 5}).get_default_values()
        dom = utils.new_document('', settings)
        parser.parse(docstring, dom)

        # Convert to a beautiful soup document tree. Note, this may not work
        # on raspbian. If it complains, just remove the "html5lib" argument
        # and put up with the warning.
        dom = bs4.BeautifulSoup(str(dom)).find('document')

        # Removes all system messages Sphinx crapped out into the docstring.
        for error in dom.find_all('system_message'):
            error.replace_with(bs4.Tag(name='empty'))

        for problematic in dom.find_all('problematic'):
            string = problematic.text
            string = re.sub(r':\w+:`', '', string).replace('`', '')

            tag = bs4.NavigableString(string)
            problematic.replace_with(tag)

        params = {}
        returns = None
        raises = None
        other_fields = []

        field_list = dom.find('field_list')

        if field_list:
            fields: typing.List[bs4.Tag] = field_list.find_all('field')
            for field in fields:
                name = field.find('field_name').text
                body = field.find('field_body').text

                if name.lower() in ('raises', 'raise', 'throws', 'throw'):
                    raises = body
                elif name.lower() in ('return', 'returns'):
                    returns = body
                elif name.lower().startswith('param '):
                    name = name[len('param '):].strip()
                    params[name] = body
                else:
                    other_fields.append((name, body))

            # Now remove the field list from the DOM so we don't see it when
            # we stringify the body.
            field_list.replace_with(bs4.Tag(name='empty'))

        body = []

        was_prev_term = False

        for child in dom.recursiveChildGenerator():
            try:
                if child.name == 'term':
                    body.append(child.text)

                    was_prev_term = True
                else:
                    if child.name == 'title':
                        title = child.text
                        title += ('\n' + '-' * len(title) + '\n')
                        title = '\n' + title

                        body.append(title)
                        was_prev_term = False

                    # This renders definition tables correctly. It is a pain
                    # in the arse to decipher otherwise.
                    elif child.name == 'paragraph':
                        if was_prev_term:
                            text = child.text

                            # Visually indent this.
                            text = text.replace('\n', '\n    ')
                            body[-1] += f' - {text}'
                        else:
                            body.append(child.text)
                        was_prev_term = False

            except:
                trace()
                pass

        data = {
            'body': '\n'.join(body),
            'params': params,
            'returns': returns,
            'raises': raises,
            'other_fields': other_fields
        }

        return data

    def make_cache(self) -> typing.Dict[str, typing.Any]:
        """
        Creates a cache dict and returns it.
        """
        try:
            walker = module_walker.ModuleWalker(self._name, self._rel)
            module_hash = module_hasher.get_module_hash(walker.start)
            attrs = [attr for attr in walker]

            # Holds our metadata.
            attr_meta = {}

            data = {
                "hash": module_hash,
                'hashing_algorithm': module_hasher.hash_alg,
                "root": walker.start.__name__,
                "attrs": attr_meta
            }
        except:
            trace()
            return {}

        for apparent_name, real_name, obj in attrs:
            # This is best effort. Some components may well error as we traverse
            # them. In this case, it is better to just skip them and try the
            # next one.
            try:
                parent, _, name = apparent_name.rpartition('.')

                try:
                    _file = self._resolve_path(real_name, obj)
                    file = _file[_file.find(walker.start.__name__):]

                    assert file != 'y'
                except:
                    file = None

                if file:
                    self._filename_cache[apparent_name] = file
                    self._filename_cache[real_name] = file

                docstring = inspect.getdoc(obj)
                if docstring:
                    docstring = inspect.cleandoc(docstring)
                    # docstring = string.remove_single_lines(docstring)
                else:
                    docstring = ''

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
                    'start_line': start_line,
                    'end_line': end_line
                }

                docstring_data = self._parse_docstring(docstring)

                attr['docstring'] = docstring_data['body']

                if inspect.ismodule(obj):
                    attr['category'] = 'module'

                    if hasattr(obj, '__all__'):
                        attr['all'] = obj.__all__

                    attr['attrs'] = dir(obj)

                elif inspect.isclass(obj):
                    obj: type = obj
                    if issubclass(obj, enum.IntFlag):
                        attr['category'] = 'intflag enum'
                    elif issubclass(obj, enum.IntEnum):
                        attr['category'] = 'int enum'
                    elif issubclass(obj, enum.Flag):
                        attr['category'] = 'flag enum'
                    elif issubclass(obj, (enum.Enum, enum.EnumMeta)):
                        attr['category'] = 'enum'
                    else:
                        attr['category'] = 'class'

                    is_desc = any(f(obj) for f in
                                  (inspect.isdatadescriptor,
                                   inspect.isgetsetdescriptor,
                                   inspect.ismemberdescriptor,
                                   inspect.ismethoddescriptor))

                    if is_desc:
                        attr['category'] = attr['category'] + ' descriptor'

                    if inspect.isabstract(obj):
                        attr['category'] = 'abstract ' + attr['category']

                    if inspect.isawaitable(obj):
                        attr['category'] = 'awaitable ' + attr['category']

                    attr['bases'] = [self._qual_name(b) for b in obj.__bases__]

                    if hasattr(obj, '__init__'):
                        attr['init'] = str(inspect.signature(
                            getattr(obj, '__init__')))
                    if hasattr(obj, '__new__'):
                        attr['new'] = str(inspect.signature(
                            getattr(obj, '__new__')))

                    class_attrs = {}

                    # Only have __get__
                    class_readonly_properties = {}

                    # Have __get__ and __set__
                    class_properties = {}

                    for attr_n, kind, _, _ in inspect.classify_class_attrs(obj):
                        if not attr_n.startswith('__'):
                            # Try to determine if we have a property or not
                            # first.
                            try:
                                is_property = inspect.isdatadescriptor(obj)
                                is_property = isinstance(obj, property) \
                                              or is_property

                                if is_property:
                                    class_properties[attr_n] = kind
                                    continue
                                elif hasattr(obj, '__get__'):
                                    class_readonly_properties[attr_n] = kind
                                    continue
                            except:
                                trace()

                            class_attrs[attr_n] = kind

                    ops = _get_operators(obj)
                    if ops:
                        attr['ops'] = ops

                    if hasattr(obj, '__slots__'):
                        attr['slots'] = obj.__slots__

                    attr['attrs'] = class_attrs
                    attr['readonly_properties'] = class_readonly_properties
                    attr['properties'] = class_properties
                    mcs = type(obj)
                    attr['metaclass'] = f'{mcs.__module__}.{mcs.__qualname__}'
                elif inspect.isfunction(obj):
                    cat = 'method' if inspect.ismethod(obj) else 'function'
                    attr['category'] = cat

                    # This only picks up `async` marked coroutines, not
                    # Python3.4-style decorated `@asyncio.coroutine` ones
                    if inspect.iscoroutinefunction(obj):
                        attr['category'] = 'async coro ' + attr['category']
                        async = True
                    elif asyncio.iscoroutinefunction(obj):
                        attr['category'] = 'Python3.4 coro ' + attr['category']
                        async = True
                    else:
                        async = False

                    if inspect.isabstract(obj):
                        attr['category'] = 'abstract ' + attr['category']

                    s = inspect.signature(obj)
                    attr['hint'] = self._get_return_annotation(s)

                    sig = f'def {name} {inspect.signature(obj)!s}'

                    if async:
                        sig = 'async ' + sig

                    attr['sig'] = sig

                    if docstring_data['returns']:
                        attr['returns'] = docstring_data['returns']
                    if docstring_data['raises']:
                        attr['raises'] = docstring_data['raises']

                    param_strings = docstring_data.get('params', {})

                    params = {}

                    for param in s.parameters.values():
                        p_str = str(param)
                        name = param.name

                        annotation = _param_annotation_re.match(p_str)
                        annotation = annotation.group(1) if annotation else None
                        default = _param_default_re.match(p_str)
                        default = default.group(1) if default else None

                        result = {
                            'name': name,
                            'annotation': annotation,
                            'default': default,
                            # Type: _ParameterKind enum -> str
                            'kind': param.kind.name.replace('_', ' ').lower(),
                            'docstring': param_strings.get(name, ''),
                        }

                        params[name] = result

                    # Store params
                    attr['params'] = params
                else:
                    category = 'attribute'

                    # Try to determine if we have a property or not first.
                    try:
                        is_property = inspect.isdatadescriptor(obj)
                        is_property = isinstance(obj, property) \
                                      or is_property

                        if is_property:
                            category = 'property'
                        elif hasattr(obj, '__get__'):
                            category = 'read-only property'
                    except:
                        pass

                    # General attribute.
                    attr['category'] = category
                    try:
                        attr['str'] = str(obj)
                        attr['repr'] = repr(obj)
                    except:
                        pass

                    type_t = type(obj)
                    attr['type'] = f'{type_t.__module__}.{type_t.__qualname__}'

                attr_meta[apparent_name] = attr
            except:
                trace()

        return data
