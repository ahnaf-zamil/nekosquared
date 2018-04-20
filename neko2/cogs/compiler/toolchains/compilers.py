#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Callable asynchronous compilers.
"""
import inspect

from neko2.cogs.compiler import tools
from neko2.cogs.compiler.toolchains import coliru, r as r_compiler


# Maps human readable languages to their syntax highlighting strings.
languages = {}
# Maps a language or syntax highlighting option
docs = {}
targets = {}


def register(*names, language):
    def decorator(coro):
        languages[language.lower()] = [coro.__name__]

        clean = inspect.cleandoc(inspect.getdoc(coro) or '')
        docs[language] = clean

        for n in {coro.__name__, *names}:
            targets[n] = coro
            docs[n] = clean
            languages[language.lower()].append(n)

        return coro
    return decorator


@register(language='C')
async def c(source):
    """
    GNU C Compiler

    Note that this will compile with the `-Wall`, `-Wextra`, `-Wpedantic`,
    `-std=c11`, `-O0`, `-lm`, and `-lpthread` flags.

    Example:
    ```c
    #include <stdio.h>

    int main(void) { printf("Hello, World!\n"); }
    ```
    """
    script = (
        'gcc -Wall -Wextra -pedantic -O0 -lm -lpthread -std=c11 -o a.out '
        'main.c && ./a.out')
    cc = coliru.Coliru(script, coliru.SourceFile('main.c', source))
    return await cc.execute()


@register('c++', 'cc', language='C++')
async def cpp(source):
    """
    GNU C++ Compiler

    Note that this will compile with the `-Wall`, `-Wextra`, `-Wpedantic`,
    `-std=c++17`, `-O0`, `-lm`, `-lstdc++fs`, and `-lpthread` flags.

    Example:
    ```cpp
    #include <iostream>

    int main() { std::cout << "Hello, World!" << std::endl; }
    ```
    """
    script = (
        'g++ -Wall -Wextra -std=c++17 -pedantic -O0 -lm -lstdc++fs -lpthread '
        '-o a.out main.cpp && ./a.out')
    cc = coliru.Coliru(script, coliru.SourceFile('main.cpp', source))
    return await cc.execute()


@register('python2.7', 'py2', 'py2.7', language='Python2')
async def python2(source):
    """
    Python2.7 Interpreter

    Example:
    ```python
    print 'Hello, World'
    ```
    """
    script = 'python main.py'
    cc = coliru.Coliru(script, coliru.SourceFile('main.py', source))
    return await cc.execute()


@register('python3', 'python3.5', 'py', 'py3', 'py3.5', language='Python')
async def python(source):
    """
    Python3.5 Interpreter

    Example:
    ```python
    print('Hello, World')
    ```
    """
    script = 'python3.5 main.py'
    cc = coliru.Coliru(script, coliru.SourceFile('main.py', source))
    return await cc.execute()


@register('pl', language='PERL 5')
async def perl(source):
    """
    PERL interpreter (PERL5)

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
    script = 'perl main.pl'
    cc = coliru.Coliru(script, coliru.SourceFile('main.pl', source))
    return await cc.execute()


@register('irb', language='Ruby')
async def ruby(source):
    """
    Ruby interpreter.

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
    cc = coliru.Coliru(script, coliru.SourceFile('main.rb', source))
    return await cc.execute()


@register('shell', language='Shell')
async def sh(source):
    """
    SHell interpreter.

    Bash interpreter

    Example
    ```sh
    yes but bash is still better imo
    ```
    """
    script = 'sh main.sh'
    cc = coliru.Coliru(script, coliru.SourceFile('main.sh', source))
    return await cc.execute()


@register(language='Bash')
async def bash(source):
    """
    Bourne-Again SHell interpreter

    Example
    ```bash
    yes i like bash ok
    ```
    """
    script = 'bash main.sh'
    cc = coliru.Coliru(script, coliru.SourceFile('main.sh', source))
    return await cc.execute()


@register('gfortran', 'f08', language='Fortran 2008')
async def fortran(source):
    """
    GNU Fortran Compiler (most recent standard)

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
    script = 'gfortran main.f08'
    cc = coliru.Coliru(script, coliru.SourceFile('main.f08', source))
    return await cc.execute()


@register('gfortran90', 'f90', language='Fortran 1990')
async def fortran90(source):
    """
    GNU Fortran Compiler (1990 Standard)

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
    script = 'gfortran main.f90'
    cc = coliru.Coliru(script, coliru.SourceFile('main.f90', source))
    return await cc.execute()


@register('gfortran95', 'f95', language='Fortran 1995')
async def fortran95(source):
    """
    GNU Fortran Compiler (1995 Standard)

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
    script = 'gfortran main.f95'
    cc = coliru.Coliru(script, coliru.SourceFile('main.f95', source))
    return await cc.execute()


@register('gawk', language='GNU Awk')
async def awk(source):
    """
    GNU AWK interpreter.

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
    script = 'awk -f main.awk'
    cc = coliru.Coliru(script, coliru.SourceFile('main.awk', source))
    return await cc.execute()


@register(language='Lua')
async def lua(source):
    """
    Lua interpreter.

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
    script = 'lua main.lua'
    cc = coliru.Coliru(script, coliru.SourceFile('main.lua', source))
    return await cc.execute()


@register('makefile', language='GNU Make')
async def make(source):
    """
    GNU-make.

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
    script = 'make -f Makefile'
    # Converts four-space indentation to tab indentation.
    source = tools.fix_makefile(source)
    cc = coliru.Coliru(script, coliru.SourceFile('Makefile', source))
    return await cc.execute()


@register('cranr', language='CRAN R')
async def r(ctx, source):
    """
    Interpreter for CRAN-R.

    This supports basic data handling operations and analysis functions, as well
    as producing up to 6 graphical plots per message (limitation is to prevent
    spam).

    Note that currently you cannot reinvoke your input by editing the initial
    source code if you pick this language.

    Example:

    ```r
    x <- 1:100
    y <- x ** 2
    plot(x, y)
    ```
    """
    with ctx.typing():
        result = await r_compiler.eval_r(source)
    return result
