from neko2.cogs.py.module_walker import ModuleWalker
from neko2.cogs.py import module_hasher
from neko2.cogs.py import module_cacher
import sys


"""
modules = ['discord', 'discord.ext.commands', 'discord.utils']


tot_size = 0
for m in modules:
    walker = [r for r in ModuleWalker(m)]
    tot_size += sys.getsizeof(m)
    tot_size += sys.getsizeof(walker)

    for n, c in walker:
        if hasattr(c, '__doc__'):
            tot_size += sys.getsizeof(c.__doc__)
        print(n)
    sys.getsizeof(walker)

for var, obj in list(locals().items()):
    tot_size += sys.getsizeof(obj)
print(tot_size)
"""

mc = module_cacher.ModuleCacher('neko2')

with open('neko2.json', 'w') as fp:
    mc.make_cache(fp)