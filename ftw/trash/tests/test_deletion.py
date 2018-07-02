from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from ftw.trash.interfaces import IRestorable
from ftw.trash.interfaces import ITrashed
from ftw.trash.tests import duplicate_with_dexterity
from ftw.trash.tests import FunctionalTestCase
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized


@duplicate_with_dexterity
class TestDeletion(FunctionalTestCase):

    @browsing
    def test_deleted_content_is_marked_with_IRestorable(self, browser):
        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        self.grant('Contributor')

        folder = create(Builder('folder').within(create(Builder('folder'))))
        subfolder = create(Builder('folder').within(folder))
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(3, len(catalog.unrestrictedSearchResults()))

        browser.login().visit(folder)
        browser.click_on('Delete')
        self.assertEquals(
            'Do you really want to delete this folder and all its contents?'
            ' (This will delete a total of 2 items.)',
            plone.first_heading())

        browser.click_on('Delete')
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(3, len(catalog.unrestrictedSearchResults()))
        self.assertTrue(IRestorable.providedBy(folder), 'Folder should provide IRestorable')
        self.assertTrue(ITrashed.providedBy(folder), 'Folder should provide ITrashed')
        self.assertFalse(IRestorable.providedBy(subfolder),
                         'Subfolder should not provide IRestorable')
        self.assertTrue(ITrashed.providedBy(subfolder), 'Subfolder should provide ITrashed')

    @browsing
    def test_children_of_site_root_are_trashed_instead_of_deleted(self, browser):
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
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(1, len(catalog.unrestrictedSearchResults()))
        self.assertTrue(IRestorable.providedBy(folder), 'Folder should provide IRestorable')
        self.assertTrue(ITrashed.providedBy(folder), 'Folder should provide ITrashed')

    def test_manage_delObjects_requires_both_delete_permissions(self):
        """collective.deletepermission adapts the behavior so that a user needs both,
        "Delete objects" on the parent and "Delete portal content" on the child.

        We dont want to change security and thus want the permissions to protect our
        trashing.

        This test must work accordingly to
        ftw.trash.tests.test_installation.TestTrashNotInstalled.[test name]
        """

        self.grant('Manager')
        parent = create(Builder('folder'))
        parent.manage_permission('Delete objects', roles=['Contributor'], acquire=False)
        child = create(Builder('folder').within(parent))
        child.manage_permission('Delete portal content', roles=['Contributor'], acquire=False)
        self.assertIn(child.getId(), parent.objectIds())
        self.assertFalse(ITrashed.providedBy(parent))

        with self.assertRaises(Unauthorized):
            # Our test user with role Manager is not allowed to delete the child because
            # we have limited the permissions to "Contributor".
            parent.manage_delObjects([child.getId()])
            self.assertIn(child.getId(), parent.objectIds())
            self.assertFalse(ITrashed.providedBy(parent), 'Unauthorized user could trash content.')

        user = create(Builder('user').with_roles('Contributor', on=parent))
        with self.user(user):
            parent.manage_delObjects([child.getId()])
            self.assertIn(child.getId(), parent.objectIds())
            self.assertTrue(ITrashed.providedBy(child), 'Authorized user couldnt trash content.')
