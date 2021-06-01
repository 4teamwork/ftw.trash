from AccessControl import getSecurityManager
from OFS.interfaces import IItem
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from ftw.trash import _
from ftw.trash.interfaces import ITrashed
from zExceptions import NotFound


def prevent_accessing_trashed_content_after_traversal(event):
    context = filter(lambda item: IItem.providedBy(item), event.request.PARENTS)[0]

    if not ITrashed.providedBy(context):
        return

    if getSecurityManager().getUser().has_role('Manager'):
        IStatusMessage(event.request).addStatusMessage(
            _(u'statusmessage_content_trashed',
              default=u'The content "${title}" is trashed.',
              mapping={u'title': safe_unicode(context.Title())}),
            type='warning')
        return

    raise NotFound()
