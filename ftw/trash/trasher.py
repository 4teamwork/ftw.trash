from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.deletepermission.del_object import protect_del_objects
from ftw.trash.exceptions import NotRestorable
from ftw.trash.interfaces import IRestorable
from ftw.trash.interfaces import ITrashed
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


class Trasher(object):
    """The trasher manages trashing, restoring and deleting of objects.
    """

    def __init__(self, context):
        self.context = context
        self.catalog = getToolByName(self.context, 'portal_catalog')

    def trash(self):
        alsoProvides(self.context, IRestorable)
        self._trash_recursive(self.context)

    def restore(self):
        if not IRestorable.providedBy(self.context):
            raise NotRestorable()

        if not getSecurityManager().checkPermission('Restore trashed content', self.context):
            raise Unauthorized()

        noLongerProvides(self.context, IRestorable)
        self._restore_recursive(self.context)

    def _trash_recursive(self, obj):
        protect_del_objects(aq_parent(aq_inner(obj)), obj.getId())
        alsoProvides(obj, ITrashed)
        self.catalog.reindexObject(obj, update_metadata=0,
                                   idxs=['object_provides', 'trashed'])
        map(self._trash_recursive, obj.objectValues())

    def _restore_recursive(self, obj):
        noLongerProvides(obj, ITrashed)
        self.catalog.reindexObject(obj, update_metadata=0,
                                   idxs=['object_provides', 'trashed'])
        map(self._restore_recursive, obj.objectValues())
