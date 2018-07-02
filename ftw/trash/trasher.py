from ftw.trash.interfaces import IRestorable
from ftw.trash.interfaces import ITrashed
from functools import partial
from zope.interface import alsoProvides


class Trasher(object):
    """The trasher manages trashing, restoring and deleting of objects.
    """

    def __init__(self, context):
        self.context = context

    def trash(self):
        alsoProvides(self.context, IRestorable)
        self._map_recursive(lambda obj: alsoProvides(obj, ITrashed), self.context)

    def _map_recursive(self, func, context):
        func(context)
        map(partial(self._map_recursive, func), context.objectValues())
