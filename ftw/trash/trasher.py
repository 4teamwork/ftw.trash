from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.deletepermission.del_object import protect_del_objects
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
        protect_del_objects(aq_parent(aq_inner(self.context)), self.context.getId())
        alsoProvides(self.context, IRestorable)
        self._map_recursive(lambda obj: alsoProvides(obj, ITrashed), self.context)

    def _map_recursive(self, func, context):
        func(context)
        map(partial(self._map_recursive, func), context.objectValues())
