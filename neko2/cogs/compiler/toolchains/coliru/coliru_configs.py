#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Callable asynchronous compilers provided by Coliru.

Reverse engineered from: http://coliru.stacked-crooked.com/

https://docs.google.com/document/d/18md3rLdgD9f5Wro3i7YYopJBFb_6MPCO8-0ihtxHoyM

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
import textwrap
import requests

from .api import *
from neko2.shared import ioutil, traits


# Thank asottile for this!
asottile_base = 'https://raw.githubusercontent.com/asottile'
ffstring_url = asottile_base + '/future-fstrings/master/future_fstrings.py'
trt_url = asottile_base + '/tokenize-rt/master/tokenize_rt.py'
ffstring_src = requests.get(ffstring_url).text
trt_src = requests.get(trt_url).text

# Thank me for this!
with open(ioutil.in_here('replify.py')) as fp:
    replify_src = fp.read()
del fp, trt_url, ffstring_url, asottile_base


# Maps human readable languages to their syntax highlighting strings.
languages = {}
# Maps a language or syntax highlighting option to the docstring.
docs = {}
# Maps a language or syntax highlighting option
targets = {}


def register(*names, language):
    import inspect

    def decorator(coro):
        languages[language.lower()] = [coro.__name__]

        unclean = inspect.getdoc(coro)
        
        if not unclean:
            unclean = 'No detailed info exists for this right now.'
        clean = inspect.cleandoc(unclean)

        docs[language] = clean

        for n in {coro.__name__, *names}:
            targets[n] = coro
            docs[n] = clean
            languages[language.lower()].append(n)

        return coro

    return decorator


@register(language='C')
async def c(source):
    """LLVM Clang C compiler

    Note that this will compile with the `-Wall`, `-Wextra`, `-Wpedantic`,
    `-std=c11`, and `-O0` flags.

    Example:
    ```c
    #include <stdio.h>

    int main(void) { printf("Hello, World!\n"); }
    ```

    Pragmas:
    
    Neko supports a few pragmas to enable some flags and features.
    Each have the syntax `#pragma neko [flag]`
    
    - `32` - force 32 bit binary output (default is 64 bit).
    - `asm` - dump assembly output.
    - `gcc` - compile under `gcc`. The default is to use `clang`.
    - `math` - compile with `-lm`.
    - `pthread` - compile with `-lpthread`.
    """
    script = '-Wall -Wextra -Wno-unknown-pragmas -pedantic -g -O0 -std=c11 -o a.out main.c '
    
    lines = source.split('\n')
    
    if '#pragma neko math' in lines:
        script += '-lm '
     
    if '#pragma neko pthread' in lines:
        script += '-lpthread '
    
    if '#pragma neko 32' in lines:
        script += '-m32 '
        
    if '#pragma neko asm' in lines:
        script += '-S -Wa,-ashl && cat -n a.out'
    else:
        script += ' && (./a.out; echo "Returned $?")'

    if '#pragma neko gcc' not in lines:
        if not source.endswith('\n'):
            source += '\n'
        compiler = 'clang '
    else:
        compiler = 'gcc '
        
    compiler_invocation = compiler + script
    script = f'echo "# {compiler_invocation}"; set -x; {compiler_invocation}'   

    cc = Coliru(script, SourceFile('main.c', source))
    sesh = await traits.CogTraits.acquire_http()
    return await cc.execute(sesh)


@register('c++', 'cc', language='C++')
async def cpp(source):
    """LLVM C++ compiler

    Note that this will compile with the `-Wall`, `-Wextra`, `-Wpedantic`,
    `-std=c++14`, `-O0`, `-lm`, `-lstdc++fs`, and `-lpthread` flags by
    default. If G++ is specified, we use `-std=c++17`.

    Example:
    ```cpp
    #include <iostream>

    int main() { std::cout << "Hello, World!" << std::endl; }
    ```
    
    Pragmas:
    
    Neko supports a few pragmas to enable some flags and features.
    Each have the syntax `#pragma neko [flag]`
    
    - `32` - force 32 bit binary output (default is 64 bit).
    - `asm` - dump assembly output.
    - `fs` - compile with the `-lstdc++fs` flag.
    - `gcc` or `g++` - compile under `g++` using `-std=c++17`. The
        default is to use `clang++` and `-std=c++14`.
    - `math` - compile with `-lm`.
    - `pthread` - compile with `-lpthread`.
    """
    script = '-Wall -Wextra -Wno-unknown-pragmas -pedantic -g -O0 -o a.out main.cpp '
    
    lines = source.split('\n')
    
    if '#pragma neko gcc' in lines or '#pragma neko g++' in lines:
        script += '-std=c++17 '
        compiler = 'g++ '
    else:
        script += '-std=c++14 '
        compiler = 'clang++ -gdwarf-2 '
        
    if '#pragma neko fs' in lines:
        script += '-lstdc++fs '
    
    if '#pragma neko math' in lines:
        script += '-lm '
     
    if '#pragma neko pthread' in lines:
        script += '-lpthread '
    
    if '#pragma neko 32' in lines:
        script += '-m32 '
    
    if '#pragma neko asm' in lines:
        script += ' -S -Wa,-ashl'
        execute = 'cat -n ./a.out'
    else:
        execute = './a.out'

    compiler_invocation = compiler + script
    
    main = SourceFile('main.cpp', source)
    make = SourceFile('Makefile', f'all:\n\t{compiler_invocation}\n\t{execute}\n')

    cc = Coliru('make', make, main)
    sesh = await traits.CogTraits.acquire_http()
    return await cc.execute(sesh)


@register('python2.7', 'py2', 'py2.7', language='Python2')
async def python2(source):
    """Python2.7 Interpreter

    Example:
    ```python
    print 'Hello, World'
    ```
    """
    script = 'python main.py; echo "Returned $?"'
    cc = Coliru(script, SourceFile('main.py', source))
    sesh = await traits.CogTraits.acquire_http()
    return await cc.execute(sesh)


@register('python3', 'python3.5', 'py', 'py3', 'py3.5', language='Python')
async def python(source):
    """Python3.5 Interpreter (complete with f-string backport support!)

    Example:
    ```python
    print('Hello, World')
    ```
    
    Add the `# repl` comment as the first line to enable interactive
    interpreter behaviour (I am still working on this, so 

    See <https://github.com/asottile/future-fstrings> and
    <https://github.com/asottile/tokenize-rt> for more details on
    how the f-string support is backported and implemented.
    """
    sesh = await traits.CogTraits.acquire_http()
    
    source_files = [
        SourceFile('main.py', source),
        SourceFile('tokenize_rt.py', trt_src),
        SourceFile('future_fstrings.py', ffstring_src)
    ]
    
    if any(source.strip().startswith(x) for x in ('#repl\n', '# repl\n', '#repr\n', '# repr\n')):
        source_files.append(SourceFile('replify.py', replify_src))
        script = 'echo "Trying experimental REPL support!"; ' \
                 'python3.5 future_fstrings.py main.py | python3.5 replify.py; ' \
                 'echo "Returned $?"'
    else:
        script = 'python3.5 future_fstrings.py main.py | python3.5; ' \
                 'echo "Returned $?"'
    
    cc = Coliru(script, *source_files)

    return await cc.execute(sesh)


@register('pl', language='PERL 5')
async def perl(source):
    """PERL interpreter (PERL5)

    Example:
    ```perl
    use warnings;
    use strict;

    my @a = (1..10);
    my $sum = 0;

    $sum += $_ for @a;
    print $sum;
    print "\n";
    ```
    """
    sesh = await traits.CogTraits.acquire_http()
    script = 'perl main.pl'
    cc = Coliru(script, SourceFile('main.pl', source))
    return await cc.execute(sesh)


@register('irb', language='Ruby')
async def ruby(source):
    """Ruby interpreter.

    Example
    ```ruby
    def translate str
      alpha = ('a'..'z').to_a
      vowels = %w[a e i o u]
      consonants = alpha - vowels

      if vowels.include?(str[0])
        str + 'ay'
      elsif consonants.include?(str[0]) && consonants.include?(str[1])
        str[2..-1] + str[0..1] + 'ay'
      elsif consonants.include?(str[0])
        str[1..-1] + str[0] + 'ay'
      else
        str # return unchanged
      end
    end

    puts translate 'apple' # => "appleay"
    puts translate 'cherry' # => "errychay"
    puts translate 'dog' # => "ogday"
    ```
    """
    script = 'ruby main.rb'
    cc = Coliru(script, SourceFile('main.rb', source))
    sesh = await traits.CogTraits.acquire_http()
    return await cc.execute(sesh)


@register('shell', language='Shell')
async def sh(source):
    """Shell interpreter.

    Example
    ```sh
    yes but bash is still better imo
    ```
    """
    script = 'sh main.sh; echo "Returned $?"'
    cc = Coliru(script, SourceFile('main.sh', source))
    sesh = await traits.CogTraits.acquire_http()
    return await cc.execute(sesh)


@register(language='Bash')
async def bash(source):
    """Bash interpreter

    Example
    ```bash
    yes i like bash ok
    ```
    """
    script = 'bash main.sh; echo "Returned $?"'
    cc = Coliru(script, SourceFile('main.sh', source))
    sesh = await traits.CogTraits.acquire_http()
    return await cc.execute(sesh)


# Fortran libs are missing... go figure.

#@register('gfortran', 'f08', language='Fortran 2008')
async def fortran(source):
    """GNU Fortran Compiler (most recent standard)

    This compiles the given code to Fortran using the 2008 standard.

    For support for F95 and F90, see the help for `Fortran 1990` and
    `Fortran 1995`.

    Example:
    ```fortran
    PROGRAM    Fibonacci
        IMPLICIT   NONE
        INTEGER :: FIRST, SECOND, TEMP, IX
        FIRST = 0
        SECOND = 1
        WRITE (*,*) FIRST
        WRITE (*,*) SECOND
        DO IX = 1, 45, 1
            TEMP = FIRST + SECOND
            FIRST = SECOND
            SECOND = TEMP
            WRITE (*,*) TEMP
        END DO
    END PROGRAM Fibonacci
    ```
    """
    script = 'gfortran main.f08 && ./a.out; echo "Returned $?"'
    cc = Coliru(script, SourceFile('main.f08', source))
    sesh = await traits.CogTraits.acquire_http()
    return await cc.execute(sesh)


#@register('gfortran90', 'f90', language='Fortran 1990')
async def fortran90(source):
    """GNU Fortran Compiler (1990 Standard)

    Example:
    ```fortran
    PROGRAM    Fibonacci
        IMPLICIT   NONE
        INTEGER :: FIRST, SECOND, TEMP, IX
        FIRST = 0
        SECOND = 1
        WRITE (*,*) FIRST
        WRITE (*,*) SECOND
        DO IX = 1, 45, 1
            TEMP = FIRST + SECOND
            FIRST = SECOND
            SECOND = TEMP
            WRITE (*,*) TEMP
        END DO
    END PROGRAM Fibonacci
    ```
    """
    script = 'gfortran main.f90 && ./a.out; echo "Returned $?"'
    cc = Coliru(script, SourceFile('main.f90', source))
    sesh = await traits.CogTraits.acquire_http()
    return await cc.execute(sesh)


#@register('gfortran95', 'f95', language='Fortran 1995')
async def fortran95(source):
    """GNU Fortran Compiler (1995 Standard)

    Example:
    ```fortran
    PROGRAM    Fibonacci
        IMPLICIT   NONE
        INTEGER :: FIRST, SECOND, TEMP, IX
        FIRST = 0
        SECOND = 1
        WRITE (*,*) FIRST
        WRITE (*,*) SECOND
        DO IX = 1, 45, 1
            TEMP = FIRST + SECOND
            FIRST = SECOND
            SECOND = TEMP
            WRITE (*,*) TEMP
        END DO
    END PROGRAM Fibonacci
    ```
    """
    script = 'gfortran main.f95 && ./a.out; echo "Returned $?"'
    cc = Coliru(script, SourceFile('main.f95', source))
    sesh = await traits.CogTraits.acquire_http()
    return await cc.execute(sesh)


@register('gawk', language='GNU Awk')
async def awk(source):
    """GNU AWK interpreter.

    Example:
    ```awk
    function factorial(n, i, f) {
        f = n
        while (--n > 1)
            f *= n
        return f
    }

    BEGIN { for (i=1; i<20; i++) print i, factorial(i) }
    ```
    """
    script = 'awk -f main.awk; echo "Returned $?"'
    cc = Coliru(script, SourceFile('main.awk', source))
    sesh = await traits.CogTraits.acquire_http()
    return await cc.execute(sesh)


@register(language='Lua')
async def lua(source):
    """Lua interpreter.

    Example:
    ```lua
    function factorial(n)
        if (n == 0) then
            return 1
        else
            return n * factorial(n - 1)
        end
    end

    for n = 0, 16 do
        io.write(n, "! = ", factorial(n), "\n")
    end
    ```
    """
    script = 'lua main.lua; echo "Returned $?"'
    cc = Coliru(script, SourceFile('main.lua', source))
    sesh = await traits.CogTraits.acquire_http()
    return await cc.execute(sesh)


@register('makefile', language='GNU Make')
async def make(source):
    """GNU-make.

    Allows you to write a basic Makefile and execute it. Note that Makefiles
    require tab indentation to work. The workaround for this drawback is to
    use four-space indentation in your code. I will then convert it to tab
    indentation for you before running it.

    Example:
    ```makefile
    CC := clang
    CFLAGS := -Wall -Wextra -pedantic -Werror -std=c11 -ggdb -gdwarf-2 -O0
    OUT := foo.out
    INFILES := main.c foo.c bar.c baz.c
    OBJFILES := $(subst .c,.o,$(INFILES))

    all: $(OBJFILES)
        $(CC) $(CFLAGS) -o $(OUT) $(OBJFILES)

    %.o: %.c %.h
        $(CC) $(CFLAGS) -o $@ -c $<

    clean:
        $(RM) *.o *.out -Rvf

    rebuild: clean all

    .PHONY: all clean rebuild
    ```
    """
    script = 'make -f Makefile; echo "Returned $?"'
    cc = Coliru(script, SourceFile('Makefile', source))
    sesh = await traits.CogTraits.acquire_http()
    return await cc.execute(sesh)
