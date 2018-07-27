from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.trash.tests import FunctionalTestCase
from ftw.trash.trasher import Trasher


class TestZMI(FunctionalTestCase):

    @browsing
    def test_delete_from_ZMI_does_actually_delete_content(self, browser):
        self.grant('Manager')

        folder = create(Builder('folder').within(create(Builder('folder'))))
        subfolder = create(Builder('folder').within(folder))
        self.assertIn(subfolder.getId(), folder.objectIds())

        browser.login().open(folder, view='manage_main')
        self.assertEquals([('folder', 'folder')], browser.find('ids:list').options)
        browser.fill({'ids:list': 'folder'}).find('Delete').click()
        self.assertNotIn(subfolder.getId(), folder.objectIds())

    @browsing
    def test_manager_can_delete_trashed_content(self, browser):
        self.grant('Manager')

        folder = create(Builder('folder').within(create(Builder('folder'))))
        create(Builder('folder').within(folder).titled(u'Normal Folder'))
        Trasher(create(Builder('folder').within(folder).titled(u'Trashed Folder'))).trash()
        self.assertItemsEqual(['normal-folder', 'trashed-folder'], folder.objectIds())

        browser.login().open(folder, view='manage_main')
        self.assertEquals([('normal-folder', 'normal-folder'),
                           ('trashed-folder', 'trashed-folder')],
                          browser.find('ids:list').options)

        browser.fill({'ids:list': 'trashed-folder'}).find('Delete').click()
        self.assertItemsEqual(['normal-folder'], folder.objectIds())
