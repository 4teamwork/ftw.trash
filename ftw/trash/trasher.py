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
        self._trash_recursive(self.context, is_root=True)

    def is_restorable(self):
        parent = aq_parent(aq_inner(self.context))
        if ITrashed.providedBy(parent):
            # Cannot restore an object when the parent is still trashed.
            return False

        return ITrashed.providedBy(self.context)

    def restore(self):
        if not self.is_restorable():
            raise NotRestorable()

        if not getSecurityManager().checkPermission('Restore trashed content', self.context):
            raise Unauthorized()

        self._restore_recursive(self.context)

    def _trash_recursive(self, obj, is_root=False):
        protect_del_objects(aq_parent(aq_inner(obj)), obj.getId())
        alsoProvides(obj, ITrashed)
        if is_root:
            alsoProvides(obj, IRestorable)
        else:
            noLongerProvides(obj, IRestorable)

        self.catalog.reindexObject(obj, update_metadata=0, idxs=['object_provides', 'trashed'])
        map(self._trash_recursive, obj.objectValues())

    def _restore_recursive(self, obj):
        noLongerProvides(obj, ITrashed)
        noLongerProvides(obj, IRestorable)
        self.catalog.reindexObject(obj, update_metadata=0, idxs=['object_provides', 'trashed'])
        map(self._restore_recursive, obj.objectValues())
