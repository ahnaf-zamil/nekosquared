#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Callable asynchronous compilers.
"""
from neko2.cogs.compiler import tools
from neko2.cogs.compiler.toolchains import coliru


targets = {}


def register(*names):
    def decorator(coro):
        for n in {coro.__name__, *names}:
            targets[n] = coro
        return coro
    return decorator


@register()
async def c(source):
    script = (
        'gcc -Wall -Wextra -pedantic -O0 -lm -lpthread -std=c11 -o a.out '
        'main.c && ./a.out')
    cc = coliru.Coliru(script, coliru.SourceFile('main.c', source))
    return await cc.execute()


@register('c++', 'cc')
async def cpp(source):
    script = (
        'g++ -Wall -Wextra -std=c++17 -pedantic -O0 -lm -lstdc++fs -lpthread '
        '-o a.out main.cpp && ./a.out')
    cc = coliru.Coliru(script, coliru.SourceFile('main.cpp', source))
    return await cc.execute()


@register('python2.7')
async def python2(source):
    script = 'python main.py'
    cc = coliru.Coliru(script, coliru.SourceFile('main.py', source))
    return await cc.execute()


@register('python3', 'python3.5')
async def python(source):
    script = 'python3.5 main.py'
    cc = coliru.Coliru(script, coliru.SourceFile('main.py', source))
    return await cc.execute()


@register('pl')
async def perl(source):
    script = 'perl main.pl'
    cc = coliru.Coliru(script, coliru.SourceFile('main.pl', source))
    return await cc.execute()


@register('pl6')
async def perl6(source):
    script = 'perl6 main.pl'

    cc = coliru.Coliru(script, coliru.SourceFile('main.pl', source))
    return await cc.execute()


@register('irb')
async def ruby(source):
    script = 'ruby main.rb'
    cc = coliru.Coliru(script, coliru.SourceFile('main.rb', source))
    return await cc.execute()


@register('shell')
async def sh(source):
    script = 'sh main.sh'
    cc = coliru.Coliru(script, coliru.SourceFile('main.sh', source))
    return await cc.execute()


@register()
async def bash(source):
    script = 'bash main.sh'
    cc = coliru.Coliru(script, coliru.SourceFile('main.sh', source))
    return await cc.execute()


@register('gfortran')
async def fortran(source):
    script = 'gfortran main.f'
    cc = coliru.Coliru(script, coliru.SourceFile('main.f', source))
    return await cc.execute()


@register()
async def awk(source):
    script = 'awk main'
    cc = coliru.Coliru(script, coliru.SourceFile('main', source))
    return await cc.execute()


@register()
async def haskell(source):
    script = 'runhaskell main.hs'
    cc = coliru.Coliru(script, coliru.SourceFile('main.hs', source))
    return await cc.execute()


@register()
async def lua(source):
    script = 'lua main.lua'
    cc = coliru.Coliru(script, coliru.SourceFile('main.lua', source))
    return await cc.execute()


@register()
async def make(source):
    script = 'make -f Makefile'
    # Converts four-space indentation to tab indentation.
    source = tools.fix_makefile(source)
    cc = coliru.Coliru(script, coliru.SourceFile('Makefile', source))
    return await cc.execute()

