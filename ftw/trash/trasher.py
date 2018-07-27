from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.deletepermission.del_object import protect_del_objects
from ftw.trash.events import BeforeObjectRestoredEvent
from ftw.trash.events import BeforeObjectTrashedEvent
from ftw.trash.events import ObjectRestoredEvent
from ftw.trash.events import ObjectTrashedEvent
from ftw.trash.exceptions import NotRestorable
from ftw.trash.interfaces import IIsRestoreAllowedAdapter
from ftw.trash.interfaces import IRestorable
from ftw.trash.interfaces import ITrashed
from zExceptions import Unauthorized
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import noLongerProvides


class Trasher(object):
    """The trasher manages trashing, restoring and deleting of objects.
    """

    def __init__(self, context):
        self.context = context

    def trash(self):
        notify(BeforeObjectTrashedEvent(self.context))
        self._trash_recursive(self.context, is_root=True)
        notify(ObjectTrashedEvent(self.context))

    def is_restorable(self):
        parent = aq_parent(aq_inner(self.context))
        if ITrashed.providedBy(parent):
            # Cannot restore an object when the parent is still trashed.
            return False

        if not getMultiAdapter((self.context, self.context.REQUEST), IIsRestoreAllowedAdapter):
            return False

        return ITrashed.providedBy(self.context)

    def restore(self):
        if not self.is_restorable():
            raise NotRestorable()

        if not getSecurityManager().checkPermission('Restore trashed content', self.context):
            raise Unauthorized()

        notify(BeforeObjectRestoredEvent(self.context))
        self._restore_recursive(self.context, is_root=True)
        notify(ObjectRestoredEvent(self.context))

    def _trash_recursive(self, obj, is_root=False):
        protect_del_objects(aq_parent(aq_inner(obj)), obj.getId())
        alsoProvides(obj, ITrashed)
        if is_root:
            alsoProvides(obj, IRestorable)

        obj.setModificationDate()
        obj.reindexObject(idxs=['object_provides', 'trashed', 'modified'])
        map(self._trash_recursive, obj.objectValues())

    def _restore_recursive(self, obj, is_root=False):
        if not is_root and IRestorable.providedBy(obj):
            # This child was deleted separately; stop restore recursion.
            return

        noLongerProvides(obj, ITrashed)
        noLongerProvides(obj, IRestorable)
        obj.setModificationDate()
        obj.reindexObject(idxs=['object_provides', 'trashed', 'modified'])
        map(self._restore_recursive, obj.objectValues())


@implementer(IIsRestoreAllowedAdapter)
@adapter(Interface, Interface)
def default_is_restore_allowed(context, request):
    """The default IIsRestoreAllowedAdapter requires add permission on the parent
    object for restoring objects, as the action can be compared to adding new content.
    """
    parent = aq_parent(aq_inner(context))
    return bool(getSecurityManager().checkPermission('Add portal content', parent))
