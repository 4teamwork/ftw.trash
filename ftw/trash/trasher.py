from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.deletepermission.del_object import protect_del_objects
from ftw.trash.interfaces import IRestorable
from ftw.trash.interfaces import ITrashed
from Products.CMFCore.utils import getToolByName
from zope.interface import alsoProvides


class Trasher(object):
    """The trasher manages trashing, restoring and deleting of objects.
    """

    def __init__(self, context):
        self.context = context
        self.catalog = getToolByName(self.context, 'portal_catalog')

    def trash(self):
        alsoProvides(self.context, IRestorable)
        self._trash_recursive(self.context)

    def _trash_recursive(self, obj):
        protect_del_objects(aq_parent(aq_inner(obj)), obj.getId())
        alsoProvides(obj, ITrashed)
        self.catalog.reindexObject(obj, idxs=['object_provides'], update_metadata=0)
        map(self._trash_recursive, obj.objectValues())
