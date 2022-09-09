from ftw.trash.testing import FTW_TRASH_FUNCTIONAL_TESTING

from ftw.trash.interfaces import (
    IRestorable,
    ITrashed,
)
from ftw.trash.utils import temporary_disable_trash

from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID, setRoles
from plone.testing.zope import Browser

from zExceptions import Unauthorized

import unittest


class TestDeletion(unittest.TestCase):
    layer = FTW_TRASH_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()

        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization",
            "Basic {username}:{password}".format(
                username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD
            ),
        )

    def assert_provides(self, obj, *expected):
        expected = set([_f for _f in expected if _f])
        got = {iface for iface in (IRestorable, ITrashed) if iface.providedBy(obj)}
        self.assertEquals(
            expected, got, "Unexpected interfaces provided by {!r}".format(obj)
        )

    def test_deleted_content_is_marked_with_IRestorable(self):
        '''Test already present in ftw.trash.tests.test_trasher'''

    def test_children_of_site_root_are_trashed_instead_of_deleted(self):
       '''Test already present in ftw.trash.tests.test_trasher '''

    def test_manage_delObjects_requires_both_delete_permissions(self):
        """collective.deletepermission adapts the behavior so that a user needs both,
        "Delete objects" on the parent and "Delete portal content" on the child.

        We dont want to change security and thus want the permissions to protect our
        trashing.

        This test must work accordingly to
        ftw.trash.tests.test_installation.TestTrashNotInstalled.[test name]
        """

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        parent = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        parent.manage_permission("Delete objects", roles=["Contributor"], acquire=False)
        
        child = api.content.create(
            container=parent,
            type="Folder",
            id="bar",
            title="Bar",
        )

        child.manage_permission(
            "Delete portal content", roles=["Contributor"], acquire=False
        )

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

    def test_manage_delObjects_does_not_check_permissions_recursively(self):
        """The standard behavior of Plone is that it only checks the delete permission on the
        content selected for deletion by the user. The children of the selected content is
        not checked for the delete permission.
        ftw.trash should not change the default behavior of Plone regarding security checks.
        """
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        parent = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        child = api.content.create(
            container=parent,
            type="Folder",
            id="bar",
            title="Bar",
        )

        child.manage_permission('Delete portal content', roles=[], acquire=False)
        self.assertIn(child.getId(), parent.objectIds())
        self.assert_provides(parent, None)
        self.assert_provides(child, None)

        with self.assertRaises(Unauthorized):
            # The child should not be deletable, as nobody has the "Delete portal content" permission.
            parent.manage_delObjects([child.getId()])

        self.assert_provides(parent, None)
        self.assert_provides(child, None)

    def test_trash_provides_manage_immediatelyDeleteObjects_method_on_portal(self):
        
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
        
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )

        folder_id = folder.id

        self.assertIn(folder_id, self.portal.objectIds())
        self.portal.manage_immediatelyDeleteObjects(folder_id)
        self.assertNotIn(folder_id, self.portal.objectIds())

    def test_trash_provides_manage_immediatelyDeleteObjects_method_on_folder(self):
        
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
        
        parent = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        folder = api.content.create(
            container=parent,
            type="Folder",
            id="bar",
            title="Bar",
        )

        folder_id = folder.id

        self.assertIn(folder_id, parent.objectIds())

        parent.manage_immediatelyDeleteObjects(folder_id)
        self.assertNotIn(folder_id, parent.objectIds())

    def test_trash_immediately_if_env_var_is_there(self):
        
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        
        container1 = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )

        container_id = container1.id

        with temporary_disable_trash():
            self.portal.manage_delObjects([container1.getId()])
            self.assertNotIn(container_id, self.portal.objectIds())
        
        container2 = api.content.create(
            container=self.portal,
            type="Folder",
            id="bar",
            title="Bar",
        )
        
        self.portal.manage_delObjects([container2.getId()])
        self.assert_provides(container2, IRestorable, ITrashed)
