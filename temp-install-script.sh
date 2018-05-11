#!/bin/bash
function main() {
    trap 'pkill python3.6; exit' INT
    source venv/bin/activate
    python3.6 -m pip install --upgrade pip

    if python3.6 -c "import aiofiles" > /dev/null 2>&1; then
        echo Already installed aiofiles

    else
        python3.6 -m pip install aiofiles
    fi
    if python3.6 -c "import aiohttp" > /dev/null 2>&1; then
        echo Already installed aiohttp

    else
        python3.6 -m pip install aiohttp
    fi
    if python3.6 -c "import asyncpg" > /dev/null 2>&1; then
        echo Already installed asyncpg

    else
        python3.6 -m pip install asyncpg
    fi
    if python3.6 -c "import bs4" > /dev/null 2>&1; then
        echo Already installed beautifulsoup4

    else
        python3.6 -m pip install beautifulsoup4
    fi
    if python3.6 -c "import cached_property" > /dev/null 2>&1; then
        echo Already installed cached_property

    else
        python3.6 -m pip install cached_property
    fi
    if python3.6 -c "import youtube_dl" > /dev/null 2>&1; then
        echo Already installed youtube_dl

    else
        python3.6 -m pip install youtube_dl
    fi
    if python3.6 -c "import dataclasses" > /dev/null 2>&1; then
        echo Already installed dataclasses

    else
        python3.6 -m pip install dataclasses
    fi
    if python3.6 -c "import PIL" > /dev/null 2>&1; then
        echo Already installed pillow

    else
        python3.6 -m pip install pillow
    fi
    if python3.6 -c "import uvloop" > /dev/null 2>&1; then
        echo Already installed uvloop

    else
        python3.6 -m pip install uvloop
    fi
    if python3.6 -c "import wordnik" > /dev/null 2>&1; then
        echo Already installed wordnik-py3

    else
        python3.6 -m pip install wordnik-py3
    fi
    if python3.6 -c "import yaml" > /dev/null 2>&1; then
        echo Already installed pyyaml

    else
        python3.6 -m pip install pyyaml
    fi
    if python3.6 -c "import docutils" > /dev/null 2>&1; then
        echo Already installed docutils

    else
        python3.6 -m pip install docutils
    fi
    if python3.6 -c "import sphinx" > /dev/null 2>&1; then
        echo Already installed sphinx

    else
        python3.6 -m pip install sphinx
    fi
    if python3.6 -c "import discord.py" > /dev/null 2>&1; then
        echo Already installed git+https://github.com/rapptz/discord.py@rewrite#egg=discord.py[voice]

    else
        python3.6 -m pip install git+https://github.com/rapptz/discord.py@rewrite#egg=discord.py[voice]
    fi
}

time main