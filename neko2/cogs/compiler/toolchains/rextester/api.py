#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Rextester API implementation.

Reverse engineered from: http://rextester.com/

===

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from typing import List

import aiohttp
import asyncio
import base64
from dataclasses import dataclass
import enum


# Forces simple editor in any response. Not really relevant, but required
# nonetheless. Layout forces vertical layout. Again, doesn't have much
# relevance to what we are doing.
EDITOR = 3
LAYOUT = 1


# Code endpoint to post to
ENDPOINT = 'http://rextester.com/rundotnet/Run'


# view-source:http://rextester.com/l/common_lisp_online_compiler:466
class Language(enum.IntEnum):
    """
    Language opcodes to specify which language to execute.
    """
    csharp = 1
    visual_basic = 2
    fsharp = 3
    java = 4
    python2 = 5
    gccc = 6
    gcccpp = 7
    php = 8
    pascal = 9
    objc = 10
    haskell = 11
    ruby = 12
    perl = 13
    lua = 14
    assembly = 15
    sqlserver = 16
    clientside_javascript = 17
    commonlisp = 18
    prolog = 19
    go = 20
    scala = 21
    scheme = 22
    nodejs = 23
    python3 = 24
    octave = 25
    clangc = 26
    clangcpp = 27
    visualcpp = 28
    visualc = 29
    d = 30
    r = 31
    tcl = 32
    mysql = 33
    postgresql = 34
    oracle = 35
    html = 36
    swift = 37
    bash = 38
    ada = 39
    erlang = 40
    elixir = 41
    ocaml = 42
    kotlin = 43
    brainfuck = 44
    fortran = 45

    sql = postgresql
    cpp = gcccpp
    c = gccc
    python = python3
    js = nodejs
    javascript = nodejs
    clientside_js = clientside_javascript



@dataclass(repr=True)
class RextesterResponse:
    warnings: str
    errors: str
    files: List[bytes]
    stats: str
    result: str


async def execute(sesh: aiohttp.ClientSession,
                  lang: Language,
                  source: str,
                  compiler_args: str=None) -> RextesterResponse:
    """
    Executes the given source code as the given language under rextester
    :param sesh: the aiohttp session to use.
    :param lang: the language to compile as.
    :param source: the source to compile.
    :param compiler_args: optional compiler args. Only applicable for C/C++
    :return: the response.
    """
    form_args = {
        'LanguageChoiceWrapper': lang.value,
        'EditorChoiceWrapper': EDITOR,
        'LayoutChoiceWrapper': LAYOUT,
        'Program': source,
        'Input': '',
        'ShowWarnings': True,
        'Privacy': '',
        'PrivacyUsers': '',
        'Title': '',
        'SavedOutput': '',
        'WholeError': '',
        'WholeWarning': '',
        'StatsToSave': '',
        'CodeGuid': ''
    }

    if compiler_args:
        form_args['CompilerArgs'] = compiler_args

    async with sesh.post(ENDPOINT, data=form_args) as resp:
        resp.raise_for_status()

        data = await resp.json(content_type='text/html')

    return RextesterResponse(
        data['Errors'],
        data['Warnings'],
        list(map(base64.b64decode, (data['Files'] or {}).values())),
        data['Stats'],
        data['Result'])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    async def test():
        async with aiohttp.ClientSession() as cs:
            r = await execute(cs, Language.csharp, '''
                using System;
                using System.Collections.Generic;
                using System.Linq;
                using System.Text.RegularExpressions;
                
                namespace Rextester
                {
                    public class Program
                    {
                        public static void Main(string[] args)
                        {
                            Console.WriteLine("Hello, world!");
                        }
                    }
                }
                ''')

            print(repr(r))

    loop.run_until_complete(test())
