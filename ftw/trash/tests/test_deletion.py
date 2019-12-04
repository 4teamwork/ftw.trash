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
from ftw.trash.utils import temporary_disable_trash
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import isLinked
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
        self.assert_provides(folder, None)
        self.assert_provides(subfolder, None)

        browser.login().visit(folder)
        browser.click_on('Delete')
        self.assertEquals(
            'Do you really want to delete this folder and all its contents?'
            ' (This will delete a total of 2 items.)',
            plone.first_heading())
        self.assert_provides(folder, None)
        self.assert_provides(subfolder, None)

        browser.click_on('Delete')
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(3, len(catalog.unrestrictedSearchResults()))
        self.assert_provides(folder, IRestorable, ITrashed)
        self.assert_provides(subfolder, ITrashed)

    @browsing
    def test_children_of_site_root_are_trashed_instead_of_deleted(self, browser):
        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        self.grant('Contributor')

        folder = create(Builder('folder'))
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(1, len(catalog.unrestrictedSearchResults()))
        self.assert_provides(folder, None)

        browser.login().visit(folder)
        browser.click_on('Delete')

        self.assertEquals('Do you really want to delete this folder and all its contents?',
                          plone.first_heading())
        browser.click_on('Delete')
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(1, len(catalog.unrestrictedSearchResults()))
        self.assert_provides(folder, IRestorable, ITrashed)

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
        self.assert_provides(parent, None)
        self.assert_provides(child, None)

        with self.assertRaises(Unauthorized):
            # Our test user with role Manager is not allowed to delete the child because
            # we have limited the permissions to "Contributor".
            parent.manage_delObjects([child.getId()])

        self.assertIn(child.getId(), parent.objectIds())
        self.assert_provides(parent, None)
        self.assert_provides(child, None)

        user = create(Builder('user').with_roles('Contributor', on=parent))
        with self.user(user):
            parent.manage_delObjects([child.getId()])
            self.assertIn(child.getId(), parent.objectIds())
            self.assert_provides(parent, None)
            self.assert_provides(child, IRestorable, ITrashed)

    def test_manage_delObjects_does_not_check_permissions_recursively(self):
        """The standard behavior of Plone is that it only checks the delete permission on the
        content selected for deletion by the user. The children of the selected content is
        not checked for the delete permission.
        ftw.trash should not change the default behavior of Plone regarding security checks.
        """
        self.grant('Manager')
        container = create(Builder('folder'))
        parent = create(Builder('folder').within(container))
        child = create(Builder('folder').within(parent))
        child.manage_permission('Delete portal content', roles=[], acquire=False)
        self.assertIn(child.getId(), parent.objectIds())
        self.assert_provides(container, None)
        self.assert_provides(parent, None)
        self.assert_provides(child, None)

        with self.assertRaises(Unauthorized):
            # The child should not be deletable, as nobody has the "Delete portal content" permission.
            parent.manage_delObjects([child.getId()])

        self.assert_provides(container, None)
        self.assert_provides(parent, None)
        self.assert_provides(child, None)

        # The parent is deletable and also deletes the child implicitly.
        container.manage_delObjects([parent.getId()])
        self.assert_provides(container, None)
        self.assert_provides(parent, IRestorable, ITrashed)
        self.assert_provides(child, ITrashed)

    def test_confirmation_dialog_link_integrity_checker_should_actually_delete_the_object(self):
        """The confirmation dialog deletes the object within a later rolled-back savepoint
        in order to detect broken links.
        If we only trash the object, the link checker will no longer work.
        Therefore ftw.trash must back off while within the link integrity checker.
        """
        if self.is_dexterity:
            # the test does not work with dexterity.
            return

        self.grant('Site Administrator')
        target = create(Builder('folder'))
        # be aware that the page object is always archetypes.
        create(Builder('page')
               .having(text='<p><a href="resolveuid/{}">folder</a>'.format(IUUID(target))))

        self.assertTrue(isLinked(target))

    def test_trash_provides_manage_immediatelyDeleteObjects_method_on_portal(self):
        self.grant('Site Administrator')
        folder_id = create(Builder('folder')).getId()
        self.assertIn(folder_id, self.portal.objectIds())
        self.portal.manage_immediatelyDeleteObjects(folder_id)
        self.assertNotIn(folder_id, self.portal.objectIds())

    def test_trash_provides_manage_immediatelyDeleteObjects_method_on_folder(self):
        self.grant('Site Administrator')
        parent = create(Builder('folder').titled(u'Parent'))
        folder_id = create(Builder('folder').within(parent)).getId()
        self.assertIn(folder_id, parent.objectIds())
        parent.manage_immediatelyDeleteObjects(folder_id)
        self.assertNotIn(folder_id, parent.objectIds())

    def test_trash_immediately_if_env_var_is_there(self):
        self.grant('Manager')

        container1 = create(Builder('folder'))
        container_id = container1.getId()

        with temporary_disable_trash():
            self.portal.manage_delObjects([container1.getId()])
            self.assertNotIn(container_id, self.portal.objectIds())

        container2 = create(Builder('folder'))
        self.portal.manage_delObjects([container2.getId()])
        self.assert_provides(container2, IRestorable, ITrashed)
