from AccessControl import getSecurityManager
from AccessControl.requestmethod import postonly
from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.trash import _
from ftw.trash.interfaces import IRestorable
from ftw.trash.interfaces import ITrashed
from ftw.trash.trasher import Trasher
from ftw.trash.utils import filter_children_in_paths
from itertools import imap
from plone.protect import CheckAuthenticator
from plone.protect import protect
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component.hooks import getSite


class TrashView(BrowserView):
    tempalte = ViewPageTemplateFile('templates/trash.pt')
    clean_confirmation_tempalte = ViewPageTemplateFile('templates/clean-trash-confirmation.pt')

    max_amount_of_items = 1000

    def __call__(self):
        self.request.set('disable_border', '1')
        self.portal_path = '/'.join(getSite().getPhysicalPath())
        self.can_clean_trash = getSecurityManager().checkPermission('Clean trash', self.context)
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
        parent = aq_parent(aq_inner(obj))
        if ITrashed.providedBy(parent):
            IStatusMessage(self.request).addStatusMessage(
                _(u'statusmessage_content_restore_error_parent_trashed',
                  default=(u'"${title}" cannot be restored because the parent container'
                           u' "${parent}" is also trashed.'
                           u' You need to restore the parent first.'),
                  mapping={u'title': safe_unicode(obj.Title()),
                           u'parent': safe_unicode(parent.Title())}),
                type='error')
            return self.request.response.redirect(self.context.absolute_url() + '/trash')

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

        target_url = obj.restrictedTraverse('@@plone_context_state').view_url()
        self.request.response.redirect(target_url)

    def confirm_clean_trash(self):
        """Show confirmation dialog for cleaning the trash.
        """
        self.request.set('disable_border', '1')
        return self.clean_confirmation_tempalte()

    @postonly
    @protect(CheckAuthenticator)
    def clean_trash(self, REQUEST):
        """Clean the trash by permantly deleting all trashed objects.
        """
        if self.request.form.get('cancel'):
            return self.request.response.redirect(self.context.absolute_url() + '/trash')

        elif self.request.form.get('delete'):
            if not getSecurityManager().checkPermission('Clean trash', self.context):
                raise Unauthorized()

            catalog = getToolByName(self.context, 'portal_catalog')
            query = {'object_provides': IRestorable.__identifier__, 'trashed': True}

            paths_to_delete = filter_children_in_paths(
                [brain.getPath() for brain in catalog(query)])
            for path in paths_to_delete:
                obj = self.context.restrictedTraverse(path)
                got_path = '/'.join(obj.getPhysicalPath())
                if got_path != path:
                    raise ValueError('Unexpectly found path {!r} when looking for {!r}'.format(
                        got_path, path))

                aq_parent(aq_inner(obj)).manage_immediatelyDeleteObjects([obj.getId()])

            return self.request.response.redirect(self.context.absolute_url() + '/trash')

        else:
            raise BadRequest()

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
