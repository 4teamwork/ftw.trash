from ftw.trash.interfaces import IRestorable
from itertools import imap
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component.hooks import getSite
import os.path


class TrashView(BrowserView):

    max_amount_of_items = 1000

    def __call__(self):
        self.request.set('disable_border', '1')
        self.portal_path = '/'.join(getSite().getPhysicalPath())
        return super(TrashView, self).__call__()

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
            'location': os.path.relpath(os.path.dirname(brain.getPath()), self.portal_path)}
