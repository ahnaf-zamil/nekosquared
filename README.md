# Neko²

Built from the mistakes and learnings of Neko.

## Installation

```python
# Using cURL
curl https://raw.githubusercontent.com/Espeonageon/nekosquared/master/install.py | python3.6
# Using wget
wget -qO- https://raw.githubusercontent.com/Espeonageon/nekosquared/master/install.py | python3.6
```

This downloads the installation script in the root of the repository, and
executes it. This script will clone the repository for you, set up a virtual
environment, install all virtual environment dependencies including discord.py
rewrite, and generate shell scripts for running, and updating the bot.

A sample systemd service file is also produced, as I find this useful.

You need to have `git`, `python3.6` or `python3.7`, and `pip` installed,
and have the `python3-virtualenv package installed.`

## The config files

This bot looks in the current working directory for a directory called `config`.
It will look in here for any configuration files that are needed. These
configuration files may be in INI, JSON or YAML format, depending on the most
appropriate implementation. Example config files can be found in the `ex-config`
directory of this repository.

## Brought to you by...

This project uses multiple existing dependencies to make life a bit easier and
to reduce the amount of testing that has to take place. These dependencies
come from both PyPi and non-PyPi sources.

### From PyPi

- [aiofiles](https://pypi.python.org/pypi/aiofiles) - Asyncio file I/O wrapper.
- [aiohttp](https://pypi.python.org/pypi/aiohttp) - Async HTTP wrapper.
- [asyncpg](https://pypi.python.org/pypi/asyncpg) - Async Postgres wrapper.
- [cached_property](https://pypi.python.org/pypi/cached-property) - Cached
    property decorator implementations that also include thread-safe wrappers
    and cached properties that will revalidate after a given period of time.
- [pyyaml](https://pypi.python.org/pypi/pyyaml) - YAML implementation.

### From elsewhere

- [Discord.py Rewrite](https://github.com/rapptz/discord.py/tree/rewrite) -
    The rewrite of the Discord.py API wrapper using asyncio.

## Looking for the old version?

Check it out [here](https://github.com/espeonageon/neko).
