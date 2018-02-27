from neko2.cogs.py.inspector import InspectionWalker
import sys

modules = ['discord', 'discord.ext.commands', 'discord.utils']


tot_size = 0
for m in modules:
    walker = [r for r in InspectionWalker(m)]
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