"""
A cached Sequel statement that we gather from disk.
"""
from nekosquared.shared import io   # in_here

__all__ = ('SqlQuery',)


class SqlQuery:
    """
    This acts as a SQL query object that is callable with any arguments. This
    just returns a tuple ready to dump into asyncpg.

    This is designed to support enter and aenter methods, so use as a context
    manager is also permitted if you like that sort of thing. In this case,
    it would literally just be something like::

    async with db.acquire() as conn, sql() as query:
        await conn.fetch(query, 1, 'foobar', 'baz', None)
    """
    def __init__(self, file_name, *, relative_to_here=True):
        """
        Reads the query from file, and initialises the object.

        :param file_name: file name to open.
        :param relative_to_here: defaults to true. If true, we consider the file
                to be in the same
        """
        if relative_to_here:
            file_name = io.in_here(file_name, nested_by=1)

        with open(file_name) as fp:
            query = '\n'.join(fp.readlines())

        self.text = query
        self.file_name = file_name

    def __str__(self):
        """Return the raw SQL query as it is in-file."""
        return self.text

    def __repr__(self):
        """Return machine readable representation."""
        return (f'<SqlQuery file={self.file_name!r}, '
                f'content={self.text!r}')

    def __call__(self, *args):
        """
        Returns a 2-tuple of the SQL query, and the arguments. This can then
        be passed directly into your desired parametrisation method.
        """
        return self.text, *args

    def __get__(self, instance, owner):
        """
        Accessor descriptor. Behaves in the same way as the call operator.
        """
        return self()
