from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from ftw.trash.testing import TRASH_NOT_INSTALLED_FUNCTIONAL
from ftw.trash.tests import duplicate_with_dexterity
from ftw.trash.tests import FunctionalTestCase
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized


@duplicate_with_dexterity
class TestTrashNotInstalled(FunctionalTestCase):
    layer = TRASH_NOT_INSTALLED_FUNCTIONAL

    @browsing
    def test_content_is_deleted_when_trash_not_installed(self, browser):
        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        self.grant('Contributor')

        folder = create(Builder('folder').within(create(Builder('folder'))))
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(2, len(catalog.unrestrictedSearchResults()))

        browser.login().visit(folder)
        browser.click_on('Delete')
        self.assertEquals('Do you really want to delete this folder and all its contents?',
                          plone.first_heading())
        browser.click_on('Delete')
        self.assertNotIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(1, len(catalog.unrestrictedSearchResults()))

    @browsing
    def test_site_root_content_is_deleted_when_trash_not_installed(self, browser):
        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        self.grant('Contributor')

        folder = create(Builder('folder'))
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(1, len(catalog.unrestrictedSearchResults()))

        browser.login().visit(folder)
        browser.click_on('Delete')
        self.assertEquals('Do you really want to delete this folder and all its contents?',
                          plone.first_heading())
        browser.click_on('Delete')
        self.assertNotIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(0, len(catalog.unrestrictedSearchResults()))

    def test_manage_delObjects_requires_both_delete_permissions(self):
        """collective.deletepermission adapts the behavior so that a user needs both,
        "Delete objects" on the parent and "Delete portal content" on the child.
        If this changes, we must adapt our code accordingly, therefore this test.
        So: dont only change the test but our code too.

        This test must work accordingly to
        ftw.trash.tests.test_deletion.TestDeletion.[test name]
        """

        self.grant('Manager')
        parent = create(Builder('folder'))
        parent.manage_permission('Delete objects', roles=['Contributor'], acquire=False)
        child = create(Builder('folder').within(parent))
        child.manage_permission('Delete portal content', roles=['Contributor'], acquire=False)
        self.assertIn(child.getId(), parent.objectIds())
        self.assert_provides(parent, None)

        with self.assertRaises(Unauthorized):
            # Our test user with role Manager is not allowed to delete the child because
            # we have limited the permissions to "Contributor".
            parent.manage_delObjects([child.getId()])
            self.assertIn(child.getId(), parent.objectIds())
            self.assert_provides(parent, None)

        user = create(Builder('user').with_roles('Contributor', on=parent))
        with self.user(user):
            parent.manage_delObjects([child.getId()])
            self.assertNotIn(child.getId(), parent.objectIds())
            self.assert_provides(parent, None)
