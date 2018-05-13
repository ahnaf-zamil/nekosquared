#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
API to Coliru.

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
import asyncio
import json
from typing import Dict

from dataclasses import dataclass

from .. import tools

__all__ = ('HOST', 'SourceFile', 'Coliru')

HOST = 'http://coliru.stacked-crooked.com'
SHARE_EP = '/share'
COMPILE_EP = '/compile'

SHARE_ARCHIVE_DIR = '/Archive2'
INITL_FILE_NAME = 'main.cpp'


@dataclass()
class SourceFile:
    name: str
    __code: str

    @property
    def code(self):
        """
        Gets the code. This is essentially immutable, as after the first
        access, this property gets cached for good measure.
        """
        # Implicitly fix makefiles
        is_probably_makefile = any(self.name.lower().startswith(x) for x in (
            'gnumakefile', 'makefile'))

        if is_probably_makefile:
            mf = tools.fix_makefile(self.__code)
            self.__dict__['code'] = mf
            return mf
        else:
            self.__dict__['code'] = self.__code
            return self.__code

    def __hash__(self):
        return hash(self.name + self.code)


class Coliru:
    """
    Handles "running" an instance of Coliru.
    """

    def __init__(self,
                 shell_script: str,
                 main_file: SourceFile,
                 *other_files: SourceFile,
                 verbose=False):
        self.shell_script = shell_script
        self.main_file = main_file
        self.other_files = other_files
        self.verbose = verbose

    @property
    def files(self):
        """Iterates across all the files."""
        yield self.main_file
        yield from self.other_files

    @staticmethod
    async def _share(session, file: SourceFile) -> (SourceFile, str):
        """
        Shares the given resource on Coliru and returns the path to the file on
        the file system for later use.
        """
        url = f'{HOST}{SHARE_EP}'
        data = json.dumps({
            'cmd': '',
            'src': file.code
        })

        resp = await session.post(url, data=data)

        # Raise if we have a screw-up.
        resp.raise_for_status()

        # for output "c97cd0bcdef4ce24", we would assume
        # the path would be Archive2/c9/7cd0bcdef4ce24
        identifier = (await resp.text()).strip()

        first_two, rest = identifier[:2], identifier[2:]

        return (
            file, f'{SHARE_ARCHIVE_DIR}/{first_two}/{rest}/{INITL_FILE_NAME}'
        )

    def _generate_script(self, files: Dict[SourceFile, str]) -> str:
        """
        Generates a build script. This is the given shell script from the
        constructor, but we make symbolic links to correctly named source
        code files *first*.
        :param files: mapping of File to the location the file is at. This
            should include the main file.
        :return: a bash script to build the source code.
        """

        script_lines = ['#!/bin/bash']

        for file, path in files.items():
            # Don't bother if the name is not going to change.
            if path != file.name:
                script_lines.append(f'cp {path} {file.name}')

        # Append the build script
        script_lines.append('set -x' if self.verbose else '')
        script_lines.append(self.shell_script)
        script_lines.append('set +x')

        script_lines.append('echo "# Returned ${?}"')

        return '\n'.join(script_lines)

    async def execute(self,
                      session,
                      loop=asyncio.get_event_loop()) -> str:
        """
        Collects the data we need and sends it to coliru for processing.
        This will then return a string containing the full output.
        """
        # Generate futures then await them together.
        futures = []
        for file in self.other_files:
            futures.append(loop.create_task(self._share(session, file)))

        results = await asyncio.gather(*futures, loop=loop)

        files = {file: path for file, path in results}
        files[self.main_file] = INITL_FILE_NAME

        script = self._generate_script(files)

        payload = json.dumps({
            'cmd': script,
            'src': self.main_file.code
        })

        resp = await session.post(f'{HOST}{COMPILE_EP}', data=payload)
        resp.raise_for_status()
        return await resp.text()
