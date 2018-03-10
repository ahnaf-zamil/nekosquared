#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Handles taking a basic hash of a module. This can be either a directory-based
module or a file-based module.
"""
import builtins   # Builtins. Just used to get the class def'n for Module.
import hashlib    # Hashing algorithms
import importlib  # Dynamic importing
import inspect    # Inspection
import os         # OS file path operations
import typing     # Type checking


ModuleType = type(builtins)


"""
Hashing algorithm to use.

Valid options include:
- scrypt
- blake2b  (512 bit)
- blake2s  (256 bit)
- md5
- sha1
- sha3_224
- sha3_256
- sha3_384
- sha3_512
- sha224
- sha256
- sha384
- sha512
- shake_128
- shake_256
"""
hash_alg = 'blake2b'


def find_path(module: ModuleType) -> typing.Union[None, str]:
    """
    Attempts to get the file or directory that a given module is defined in.

    If we cannot get this information, we just return None.
    """
    # noinspection PyBroadException
    try:
        file = os.path.abspath(inspect.getfile(module))

        if os.path.basename(file).startswith('__init__'):
            return os.path.dirname(file)
        else:
            return file
    except BaseException:
        return None


def __hash_file(path: str) -> bytes:
    """Hashes a specific file."""
    with open(path, 'br') as fp:
        return hashlib.new(hash_alg, fp.read()).digest()


def __get_all_files_in(path: str) -> typing.Iterator[str]:
    for root, dirs, files in os.walk(path):
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')

        for file in files:
            yield os.path.join(root, file)


def __hash_directory(path: str) -> bytes:
    """Hashes all files in the given path."""
    files = __get_all_files_in(path)

    # This may well be slow and inefficient
    data = b''
    for file in files:
        with open(file, 'br') as fp:
            data += fp.read()

    return hashlib.new(hash_alg, data).digest()


def get_module_hash(module: typing.Union[str, ModuleType],
                    rel: str=None) -> bytes:
    """
    Hashes an entire module.
    :param module: the module to hash, or the name of the module to import.
    :param rel: relative location. Only used if ``module`` is a string.
    :return: a hash. If this is not possible, 0 bytes are output. This allows
    us to still fill a hash field in the serialised cache. If we cannot resolve
    a module for whatever reason, but we do have a valid path, we hash that
    instead.

    The purpose here is to detect if the modules have changed compared to the
    hash. If they have, we know to regenerate the cache for that module.
    
    """
    if isinstance(module, str):
        module = importlib.import_module(module, rel)

    try:
        path = find_path(module)
        try:
            if os.path.isfile(path):
                return __hash_file(path)
            else:
                return __hash_directory(path)
        except BaseException:
            return hashlib.new(hash_alg, path).digest()
    except BaseException:
        return b''
