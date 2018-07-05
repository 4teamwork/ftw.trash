from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import statusmessages
from ftw.testing import freeze
from ftw.trash.interfaces import ITrashed
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

        self.assertEquals(
            [{'Last modified': 'Dec 15, 2016 05:09 PM',
              'Type': self.type_label,
              'Title': 'Delete that http://nohost/plone/parent/delete-that',
              '': ''}],
            browser.css('.trash-table').first.dicts())

    @browsing
    def test_restore_trashed_content(self, browser):
        self.grant('Site Administrator')

        folder = create(Builder('folder').titled(u'My Folder'))
        with freeze(datetime(2011, 1, 1)):
            Trasher(folder).trash()

        self.assertTrue(ITrashed.providedBy(folder))

        transaction.commit()
        browser.login().open().click_on('Trash')

        self.assertEquals(
            [{'Last modified': 'Jan 01, 2011 12:00 AM',
              'Type': self.type_label,
              'Title': 'My Folder http://nohost/plone/my-folder',
              '': ''}],
            browser.css('.trash-table').first.dicts())

        browser.css('.trash-table').find('Restore').first.click()
        statusmessages.assert_message('The content "My Folder" has been restored.')
        self.assertEqual(folder.absolute_url(), browser.url)

        transaction.begin()
        self.assertFalse(ITrashed.providedBy(folder))

    @browsing
    def test_error_message_when_restore_not_allowed(self, browser):
        self.grant('Site Administrator')

        parent = create(Builder('folder').titled(u'Parent'))
        folder = create(Builder('folder').titled(u'My Folder').within(parent))
        Trasher(folder).trash()
        parent.manage_permission('Add portal content', roles=[], acquire=False)
        transaction.commit()

        browser.login().open().click_on('Trash').click_on('Restore')
        statusmessages.assert_message(
            'You are not allowed to restore "My Folder".'
            ' You may need to change the workflow state of the parent content.')

        transaction.begin()
        self.assertTrue(ITrashed.providedBy(folder))

    @property
    def type_label(self):
        if self.is_dexterity:
            return 'dxfolder'
        else:
            return 'Folder'
