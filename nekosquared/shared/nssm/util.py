"""
(c) Espeonageon 2018.
Licensed under the Mozilla Public License V2.0

You can use this however you like under the MPLv2.0 license, but you must
make sure to keep this message here.

---

Various utility methods for NSSM.
"""
import collections


class ReversingOrderedDict:
    """
    Holds two dictionary objects. One is the mapping of key-values, provided
    in the constructor, and the other is an inferred reverse mapping of
    value-keys.

    This allows multi-directional lookup as a constant time operation, at the
    cost of more work when the object is first initialised.

    This type is designed to be immutable.

    Note that value members that are sets or lists will be split up on the
    reverse mapping so that each element in said collection maps to the same
    key. This will not occur for tuples, or frozen sets.
    """
    def __init__(self, pairs):
        self._forwards = collections.OrderedDict()
        self._backwards = collections.OrderedDict()

        for k, v in pairs.items():
            # Not sure how to deal with this, so just die.
            assert not isinstance(v, dict)

            # Lists and sets are not hashable.
            if isinstance(v, (list, set)):
                for sv in v:
                    self._backwards[sv] = k
            else:
                self._backwards[v] = k
            self._forwards[k] = v

    def get_value(self, key, **kwargs):
        if 'default' in kwargs and key not in self._forwards:
            return kwargs['default']
        else:
            return self._forwards[key]

    def get_key(self, value, **kwargs):
        if 'default' in kwargs and value not in self._backwards:
            return kwargs['default']
        else:
            return self._backwards[value]

    def items(self):
        return self._forwards.items()

    def keys(self):
        return self._forwards.keys()

    def values(self):
        return self._forwards.values()

    def len(self):
        return len(self._forwards)

    len_kv = len

    def len_vk(self):
        return len(self._backwards)

    def __str__(self):
        return str(self._forwards)

    def __repr__(self):
        return repr(self._forwards)

    def __iter__(self):
        return iter(self.keys())

    def __contains__(self, item):
        return item in self.keys()
