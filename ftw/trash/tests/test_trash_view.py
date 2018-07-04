from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from ftw.testing import freeze
from ftw.trash.tests import duplicate_with_dexterity
from ftw.trash.tests import FunctionalTestCase
from ftw.trash.trasher import Trasher
import transaction


@duplicate_with_dexterity
class TestTrashView(FunctionalTestCase):

    @browsing
    def test_view_requires_restore_permission(self, browser):
        self.grant('Contributor')
        self.portal.manage_permission('Restore trashed content', roles=[], acquire=False)
        transaction.commit()

        trash_link_label = 'Trash'

        browser.login().open()
        self.assertNotIn(trash_link_label, browser.css('#portal-personaltools li').text)
        with browser.expect_unauthorized():
            browser.open(view='trash')

        self.portal.manage_permission('Restore trashed content', roles=['Contributor'],
                                      acquire=False)
        transaction.commit()

        browser.open()
        self.assertIn(trash_link_label, browser.css('#portal-personaltools li').text)
        browser.css('#portal-personaltools li').find(trash_link_label).first.click()
        self.assertEquals(self.portal.portal_url() + '/trash', browser.url)

    @browsing
    def test_lists_only_restorable_content(self, browser):
        self.grant('Site Administrator')

        create(Builder('folder').titled(u'Keep that'))
        parent = create(Builder('folder').titled(u'Parent'))
        folder = create(Builder('folder').titled(u'Delete that').within(parent))
        create(Builder('folder').titled(u'Child of folder to be deleted').within(folder))

        with freeze(datetime(2016, 12, 15, 17, 9)):
            Trasher(folder).trash()

        transaction.commit()
        browser.login().open().click_on('Trash')
        self.assertEquals('trash', plone.view())

        if self.is_dexterity:
            type_label = 'dxfolder'
        else:
            type_label = 'Folder'

        self.assertEquals(
            [{'Last modified': 'Dec 15, 2016 05:09 PM',
              'Type': type_label,
              'Title': 'Delete that',
              'Location': 'parent'}],
            browser.css('.trash-table').first.dicts())
