# Contributing

Feel free to contribute. Just remember the following when writing code:

0. Document your code properly.
1. Python code should be space-indented by 4 spaces.
2. Lines must be less than 80 characters wide.
3. Follow PEP-8 wherever possible.
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
5. Refer to [the Google Python style guide](https://google.github.io/styleguide/pyguide.html).
6. Config files should be referred to without an extension. This allows the user
    to use the serialization format they are most comfortable with.
7. Detailed commit messages please!
