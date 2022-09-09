from ftw.trash.testing import FTW_TRASH_FUNCTIONAL_TESTING

from ftw.trash.trasher import Trasher
from ftw.trash.exceptions import NotRestorable
from ftw.trash.interfaces import (
    IRestorable,
    ITrashed,
)

from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID, setRoles
from plone.testing.zope import Browser

import transaction
import unittest

class TestTrashView(unittest.TestCase):
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

    def test_view_requires_restore_permission(self):
        '''Test already present in ftw.trash.tests.test_deletion'''

    def test_lists_only_restorable_content(self):
        '''Test already present in ftw.trash.tests.test_trasher'''

    def test_restore_trashed_content(self):
        '''Test already present in ftw.trash.tests.test_trasher'''

    def test_error_message_when_restore_not_allowed(self):

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

        Trasher(folder).trash()
        parent.manage_permission("Add portal content", roles=[], acquire=False)
        transaction.commit()

        self.browser.open(self.portal_url + "/trash")
        self.assertTrue("Bar" in self.browser.contents)

        self.browser.getControl("Restore").click()
        self.assertTrue('You are not allowed to restore "Bar"' in self.browser.contents)
        self.assert_provides(folder, IRestorable, ITrashed)


    def test_error_message_when_parent_is_trashed(self):

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

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

        Trasher(parent).trash()
        Trasher(child).trash()

        self.assert_provides(parent, IRestorable, ITrashed)
        self.assert_provides(child, IRestorable, ITrashed)
        transaction.commit()

        self.browser.open(self.portal_url + "/trash")
        with self.assertRaises(NotRestorable):
            Trasher(child).restore()
 
        transaction.begin()
        self.assert_provides(parent, IRestorable, ITrashed)
        self.assert_provides(child, IRestorable, ITrashed)


    def test_empy_trash(self):

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )

        Trasher(folder).trash()

        self.assertIn("foo", self.portal.objectIds())
        transaction.commit()

        self.browser.open(self.portal_url + "/trash")
        self.assertIn("Trash", self.browser.contents)

        self.browser.getControl("Delete permanently").click()
        self.assertNotIn("foo", self.portal.objectIds())




    def test_empty_trash_button_not_visible_without_permission(self):

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        self.browser.open(self.portal_url + "/trash")
        transaction.commit()

        self.browser.reload()
        self.assertFalse("Delete permanently" in self.browser.contents)


    
    def test_empty_trash_when_parent_and_child_are_both_trashed(self):
        """Regression test: when trying to delete a child but the parent was deleted
        bevore, an exception is raised.
        Solution: do not delete children and parents in the same set; just delete parents,
        which is recursive anyway.
        """

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

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

        Trasher(child).trash()
        Trasher(parent).trash()
        transaction.commit()

        self.browser.open(self.portal_url + "/trash")
        self.assertIn("Trash", self.browser.contents)

        self.browser.open(self.portal_url + "/trash/confirm_clean_trash")
        self.browser.getControl("Delete").click()
        self.assertNotIn("parent", self.portal.objectIds())


    def test_empty_trash_event_if_user_has_insufficient_permissions_on_the_item(
        self
    ):
    
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

        parent.manage_delObjects([folder_id])
        folder.manage_permission(
            "Delete portal content", roles=["Manager"], acquire=False
        )
        transaction.commit()

        self.browser.open(self.portal_url + "/trash")
        self.browser.open(self.portal_url + "/trash/confirm_clean_trash")
        self.browser.getControl("Delete").click()

        self.assertNotIn(folder_id, parent)

    def test_delete_single_trashed_object(self):

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        foo = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        bar = api.content.create(
            container=self.portal,
            type="Folder",
            id="bar",
            title="Bar",
        )

        self.assertIn(foo.id, self.portal)
        self.assertIn(bar.id, self.portal)

        self.portal.manage_delObjects([foo.id])
        transaction.commit()

        self.browser.open(self.portal_url + "/trash")
        self.browser.getControl("Delete permanently").click()

        self.portal.manage_delObjects([bar.id])
        transaction.commit()

        self.assertNotIn(foo.getId(), self.portal)
        self.assertIn(bar.getId(), self.portal)

