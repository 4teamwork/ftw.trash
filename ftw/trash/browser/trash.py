from AccessControl.requestmethod import postonly
from ftw.trash import _
from ftw.trash.interfaces import IRestorable
from ftw.trash.trasher import Trasher
from itertools import imap
from plone.protect import CheckAuthenticator
from plone.protect import protect
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import BadRequest
from zope.component.hooks import getSite


class TrashView(BrowserView):
    tempalte = ViewPageTemplateFile('templates/trash.pt')

    max_amount_of_items = 1000

    def __call__(self):
        self.request.set('disable_border', '1')
        self.portal_path = '/'.join(getSite().getPhysicalPath())
        return self.tempalte()

    @postonly
    @protect(CheckAuthenticator)
    def restore(self, REQUEST, uuid):
        """Restore an item by uid.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog({'UID': uuid, 'trashed': True})
        if len(brains) != 1:
            raise BadRequest()

        obj = brains[0].getObject()
        trasher = Trasher(obj)
        if not trasher.is_restorable():
            IStatusMessage(self.request).addStatusMessage(
                _(u'statusmessage_content_restore_not_allowed',
                  default=(u'You are not allowed to restore "${title}".'
                           u' You may need to change the workflow state of the parent content.'),
                  mapping={u'title': safe_unicode(obj.Title())}),
                type='error')
            return self.request.response.redirect(self.context.absolute_url() + '/trash')

        trasher.restore()
        IStatusMessage(self.request).addStatusMessage(
            _(u'statusmessage_content_restored',
              default=u'The content "${title}" has been restored.',
              mapping={u'title': safe_unicode(obj.Title())}),
            type='info')

        self.request.response.redirect(obj.absolute_url())

    def get_trashed_items(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'object_provides': IRestorable.__identifier__,
            'trashed': True,
            'sort_on': 'modified',
            'sort_order': 'reverse',
            'sort_limit': self.max_amount_of_items}

        return imap(self._brain_to_item, catalog(query)[:self.max_amount_of_items])

    def _brain_to_item(self, brain):
        return {
            'type': brain.Type,
            'modified': self.context.toLocalizedTime(brain.modified, long_format=1),
            'title': brain.Title,
            'location': brain.getURL(),
            'uuid': brain.UID}
