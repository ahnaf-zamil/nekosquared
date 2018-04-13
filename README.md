# Neko²

Built from the mistakes and learnings of Neko.

## Installation

```python
# Using cURL
curl https://raw.githubusercontent.com/neko404notfound/nekosquared/master/install.py | python3.6
# Using wget
wget -qO- https://raw.githubusercontent.com/neko404notfound/nekosquared/master/install.py | python3.6
```

This downloads the installation script in the root of the repository, and
executes it. This script will clone the repository for you, set up a virtual
environment, install all virtual environment dependencies including discord.py
rewrite, and generate shell scripts for running, and updating the bot.

A sample systemd service file is also produced, as I find this useful.

You need to have `git`, `python3.6` or `python3.7`, and `pip` installed,
and have the `python3-virtualenv package installed.`

For `py` to work, any listed modules to index must be installed. See 
`example-config/py-deps.txt` for a list of additional dependency modules
for our example.

## Running

To run the bot, you should run the following:

```bash
# On OSX, Unix, Linux
python3.6 -m neko2

# On Windows NT
py -3.6 -m neko2
```

The bot will DM you any errors that occur while the bot is starting up and 
loading any modules. To suppress this behaviour, invoke the bot with the
`--nowarnstart` flag, like so:

```bash
python3.6 -m neko2 --nowarnstart
# or
py -3.6 -m neko2 --nowarnstart
```

If you do not want any error messages sent to your inbox from the bot regarding
errors whilst the bot is physically online, then you should supply the flag
`--nowarnrun`

### The config files

The bot defaults to the config directory `../neko2config`. This is changeable
by specifying the path as the first command line option when running the bot:

```bash
python3.6 -m neko2 /home/me/my_directory
# or
python3.6 -m neko2 ~/my_directory
```

Config files can have any supported file extension, but they **must** have
one. The file type should be guessed automatically. For example, `discord` will
load either `discord.json`, `discord.py` or `discord.yaml` depending on which
is found first.

The bot currently supports the following serialization formats:

| Extension | Format | Notes |
|---|---|---|
| `.json` | JSON | Recommended. |
| `.yaml` | YAML | Yet Another Markup Language. Requires `pyyaml` to be installed. |
| `.py` | Python | Loads the file and attempts to `eval` it. This risks arbitrary code execution and is untested. | 

The current config files are required for the bot to work:

| Name | Description |
|---|---|
| `discord` | Basic Discord config and authentication. Holds a dictionary of two dictionaries: `bot` and `auth`. `bot` contains `command_prefix` (string) and `owner_id` (int); `auth` contains `client_id` (int) and `token` (string). An additional `debug` boolean config value can be supplied to enable verbose stack traces. This defaults to `false` if unspecified. The `dm_errors` parameter can also be specified to control whether errors get sent to the bot owner's inbox. This defaults to true if not specified. |
| `database` | Holds PostgreSQL credentials. This is a dictionary of four strings: `database`, `host`, `user`, and `password`. |

Cogs require the following additional configurations:

| Cog | Name | Description |
|---|---|---|
| `neko2.cogs.urlshorten` | `urlshorten` | [String API key](https://console.developers.google.com/apis/credentials) for the `goo.gl` API for URL shortening. |
| `neko2.cogs.wordnik` | `wordnik` | [String API key](http://developer.wordnik.com/) for the `wordnik` API for dictionary access. |

## Contributing

Feel free to contribute. Just remember the following when writing code:

0. Document your code properly.
1. Python code should be space-indented by 4 spaces.
2. Lines must be less than 80 characters wide.
3. Follow PEP-8 wherever possible.\*
4. Each document should be started with the following preamble. Imports should
    follow the following order, any groups of imports under the same category
    should be ordered alphabetically. The `__all__` attribute can be skipped if
    the file is a cog.

    ```python
    #!/usr/bin/env python3.6
    # -*- coding: utf-8 -*-
    """
    Description of file here.
    """
    import python.standard.library.modules   # What we use from it
    import third.party.modules               # What we use from it
    import neko2.absolute.imports            # What we use from it
    from . import relative.module            # What we use from it
    
    
    __all__ = ('SomeClass', 'some_function')
    ```

5. Refer to [the Google Python style guide](https://google.github.io/styleguide/pyguide.html)
6. Refer to [this SQL style guide](SQL_STYLE.md)
7. SQL queries should be [parameterised](https://magicstack.github.io/asyncpg/current/usage.html)
    wherever applicable. They should also be placed in their own `*.sql` file in
    the directory where they are used. You may then refer to them from a cog by
    using the following pattern. This example is for the SQL file 
    `my_sql_query.sql`. Notice that the extension is inferred.
    
    ```python
    from neko2.engine import commands
    from neko2.shared import sql
    from neko2.shared import traits
     
    
    class SomeCog(traits.PostgresPool):
        # Loads the query from the file.
        my_sql_query = sql.sql_query('my_sql_query')
 
        @commands.command()
        async def my_command(self, ctx, some_parameter):
            async with await self.acquire_db() as conn:
                result = conn.fetch(self.my_sql_query, some_parameter)
                
            row_strings = []
            for i in range(0, min(10, len(result))):
                result_row = result[i]
                string_row = ', '.join(result_row)
                row_strings.append(string_row)
                
            await ctx.send('\n'.join(row_strings))
    ```
8. Config files should be referred to without an extension. This allows the user
    to use the serialization format they are most comfortable with.
9. Detailed commit messages please!
