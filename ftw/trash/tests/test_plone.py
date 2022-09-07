from ftw.trash.testing import FTW_TRASH_INTEGRATION_TESTING
from ftw.trash.trasher import Trasher
from ftw.trash.interfaces import (
    IRestorable,
    ITrashed,
)

from plone.app.testing import TEST_USER_ID, setRoles
from plone import api

import unittest


class TestPloneIntegration(unittest.TestCase):
    layer = FTW_TRASH_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]

    def assert_provides(self, obj, *expected):
        expected = set([_f for _f in expected if _f])
        got = {iface for iface in (IRestorable, ITrashed) if iface.providedBy(obj)}
        self.assertEquals(
            expected, got, "Unexpected interfaces provided by {!r}".format(obj)
        )


    def test_folder_objectItems_returns_trashed_content(self):
        """A folder's objectItems should return trashed content.
        """
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        container = api.content.create(
            container=self.portal,
            type="Folder",
            id="parent",
            title="Parent",
        )
        
        foo = api.content.create(
            container=container,
            type="Folder",
            id="foo",
            title="Foo",
        )
        bar = api.content.create(
            container=container,
            type="Folder",
            id="bar",
            title="Bar",
        )
        self.assertEqual([("foo", foo), ("bar", bar)], list(container.objectItems()))
        
        Trasher(foo).trash()
        self.assertEqual([("foo", foo), ("bar", bar)], list(container.objectItems()))

    def test_plone_objectItems_returns_trashed_content(self):
        """A Plone site's objectItems should return trashed content.
        """
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        foo = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        self.assertIn(("foo", foo), list(self.portal.objectItems()))
        
        Trasher(foo).trash()
        self.assertIn(("foo", foo), list(self.portal.objectItems()))

    def test_folder_contentItems_does_not_return_trashed_content(self):
        """A folder's contentItems should not return trashed content.
        """
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        container = api.content.create(
            container=self.portal,
            type="Folder",
            id="parent",
            title="Parent",
        )
        foo = api.content.create(
            container=container,
            type="Folder",
            id="foo",
            title="Foo",
        )
        bar = api.content.create(
            container=container,
            type="Folder",
            id="bar",
            title="Bar",
        )
        self.assertEqual([("foo", foo), ("bar", bar)], container.contentItems())
        
        Trasher(foo).trash()
        self.assertEqual([("bar", bar)], container.contentItems())

    def test_plone_contentItems_does_not_return_trashed_content(self):
        """A Plone site's contentItems should not return trashed content.
        """
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        
        foo = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        self.assertIn(("foo", foo), self.portal.contentItems())
        
        Trasher(foo).trash()
        self.assertNotIn(("foo", foo), self.portal.contentItems())

    def test_listFolderContents_does_not_return_trashed_content(self):
        """A folder's listFolderContents should not return trashed content.
        """
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        container = api.content.create(
            container=self.portal,
            type="Folder",
            id="parent",
            title="Parent",
        )
        foo = api.content.create(
            container=container,
            type="Folder",
            id="foo",
            title="Foo",
        )
        bar = api.content.create(
            container=container,
            type="Folder",
            id="bar",
            title="Bar",
        )
        self.assertEqual([foo, bar], container.listFolderContents())
        
        Trasher(foo).trash()
        self.assertEqual([bar], container.listFolderContents())

    def test_getFolderContents_does_not_return_trashed_content(self):
        """A folder's getFolderContents should not return trashed content.
        """
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        container = api.content.create(
            container=self.portal,
            type="Folder",
            id="parent",
            title="Parent",
        )
        foo = api.content.create(
            container=container,
            type="Folder",
            id="foo",
            title="Foo",
        )
        bar = api.content.create(
            container=container,
            type="Folder",
            id="bar",
            title="Bar",
        )
        self.assertEqual(
            [foo, bar], [brain.getObject() for brain in container.getFolderContents()]
        )
        
        Trasher(foo).trash()
        self.assertEqual(
            [bar], [brain.getObject() for brain in container.getFolderContents()]
        )
