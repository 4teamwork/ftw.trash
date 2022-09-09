from ftw.trash.testing import FTW_TRASH_INTEGRATION_TESTING,FTW_TRASH_FUNCTIONAL_TESTING  # noqa: E501

from ftw.trash.trasher import Trasher
from ftw.trash.exceptions import NotRestorable
from ftw.trash.interfaces import (
          IBeforeObjectRestoredEvent,
          IBeforeObjectTrashedEvent,
          IIsRestoreAllowedAdapter,
          IObjectRestoredEvent,
          IObjectTrashedEvent,
    IRestorable,
    ITrashed,
)

from plone import api
from plone.app.testing import TEST_USER_ID, setRoles

import unittest

from zope.component import adapter, getMultiAdapter, getSiteManager
from zope.interface import Interface, implementer


class TestTrasher(unittest.TestCase):
    layer = FTW_TRASH_INTEGRATION_TESTING

    def assert_provides(self, obj, *expected):
        expected = set([_f for _f in expected if _f])
        got = {iface for iface in (IRestorable, ITrashed) if iface.providedBy(obj)}
        self.assertEquals(
            expected, got, "Unexpected interfaces provided by {!r}".format(obj)
        )

    def get_catalog_indexdata(self, obj):
        """Return the catalog index data for an object as dict."""
        self.maybe_process_indexing_queue()
        catalog = api.portal.get_tool("portal_catalog")
        rid = catalog.getrid("/".join(obj.getPhysicalPath()))
        return catalog.getIndexDataForRID(rid)

    def maybe_process_indexing_queue(self):
        from Products.CMFCore.indexing import processQueue

        processQueue()

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]

    def test_marks_trashed_page_as_trashed_and_restorable(self):

        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        
        page = api.content.create(
            container=self.portal,
            type="Document",
            id="foo",
            title="Foo",
        )

        self.assert_provides(page, None)

        Trasher(page).trash()
        self.assert_provides(page, IRestorable, ITrashed)

    def test_marks_children_of_trashed_folder_only_as_trashed(self):

        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        subfolder = api.content.create(
            container=folder, type="Folder", id="bar", title="Bar"
        )

        self.assert_provides(folder, None)
        self.assert_provides(subfolder, None)

        Trasher(folder).trash()
        self.assert_provides(folder, IRestorable, ITrashed)
        self.assert_provides(subfolder, ITrashed)

    def test_catalog_is_updated_when_trashing_content(self):

        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        subfolder = api.content.create(
            container=folder, type="Folder", id="bar", title="Bar"
        )

        self.assertFalse(self.get_catalog_indexdata(folder).get("trashed"))
        self.assertNotIn(
            ITrashed.__identifier__,
            self.get_catalog_indexdata(folder).get("object_provides"),
        )

    
        self.assertNotIn(
            IRestorable.__identifier__,
            self.get_catalog_indexdata(folder).get("object_provides"),
        )

        self.assertFalse(self.get_catalog_indexdata(subfolder).get("trashed"))
        self.assertNotIn(
            ITrashed.__identifier__,
            self.get_catalog_indexdata(subfolder).get("object_provides"),
        )

        self.assertNotIn(
            IRestorable.__identifier__,
            self.get_catalog_indexdata(subfolder).get("object_provides"),
        )

        Trasher(folder).trash()
        self.assertTrue(self.get_catalog_indexdata(folder).get("trashed"))
        self.assertIn(
            ITrashed.__identifier__,
            self.get_catalog_indexdata(folder).get("object_provides"),
        )

        self.assertIn(
            IRestorable.__identifier__,
            self.get_catalog_indexdata(folder).get("object_provides"),
        )

        self.assertTrue(self.get_catalog_indexdata(subfolder).get("trashed"))
        self.assertIn(
            ITrashed.__identifier__,
            self.get_catalog_indexdata(subfolder).get("object_provides"),
        )

        self.assertNotIn(
            IRestorable.__identifier__,
            self.get_catalog_indexdata(subfolder).get("object_provides"),
        )

    def test_restorable_content_can_be_restored(self):

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        self.assert_provides(folder, None)

        Trasher(folder).trash()
        self.assert_provides(folder, IRestorable, ITrashed)

        Trasher(folder).restore()
        self.assert_provides(folder, None)

    def test_children_are_restored_correctly(self):

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        subfolder = api.content.create(
            container=folder, type="Folder", id="bar", title="Bar"
        )
        self.assert_provides(folder, None)
        self.assert_provides(subfolder, None)

        Trasher(folder).trash()
        self.assert_provides(folder, IRestorable, ITrashed)
        self.assert_provides(subfolder, ITrashed)

        Trasher(folder).restore()
        self.assert_provides(folder, None)
        self.assert_provides(subfolder, None)

    def test_catalog_is_updated_when_restoring_content(self):

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        subfolder = api.content.create(
            container=folder, type="Folder", id="bar", title="Bar"
        )

        self.assertFalse(self.get_catalog_indexdata(folder).get("trashed"))
        self.assertNotIn(
            ITrashed.__identifier__,
            self.get_catalog_indexdata(folder).get("object_provides"),
        )
        self.assertNotIn(
            IRestorable.__identifier__,
            self.get_catalog_indexdata(folder).get("object_provides"),
        )

        self.assertFalse(self.get_catalog_indexdata(subfolder).get("trashed"))
        self.assertNotIn(
            ITrashed.__identifier__,
            self.get_catalog_indexdata(subfolder).get("object_provides"),
        )
        self.assertNotIn(
            IRestorable.__identifier__,
            self.get_catalog_indexdata(subfolder).get("object_provides"),
        )

        Trasher(folder).trash()
        self.assertTrue(self.get_catalog_indexdata(folder).get("trashed"))
        self.assertIn(
            ITrashed.__identifier__,
            self.get_catalog_indexdata(folder).get("object_provides"),
        )
        self.assertIn(
            IRestorable.__identifier__,
            self.get_catalog_indexdata(folder).get("object_provides"),
        )

        self.assertTrue(self.get_catalog_indexdata(subfolder).get("trashed"))
        self.assertIn(
            ITrashed.__identifier__,
            self.get_catalog_indexdata(subfolder).get("object_provides"),
        )
        self.assertNotIn(
            IRestorable.__identifier__,
            self.get_catalog_indexdata(subfolder).get("object_provides"),
        )

        Trasher(folder).restore()
        self.assertFalse(self.get_catalog_indexdata(folder).get("trashed"))
        self.assertNotIn(
            ITrashed.__identifier__,
            self.get_catalog_indexdata(folder).get("object_provides"),
        )
        self.assertNotIn(
            IRestorable.__identifier__,
            self.get_catalog_indexdata(folder).get("object_provides"),
        )

        self.assertFalse(self.get_catalog_indexdata(subfolder).get("trashed"))
        self.assertNotIn(
            ITrashed.__identifier__,
            self.get_catalog_indexdata(subfolder).get("object_provides"),
        )
        self.assertNotIn(
            IRestorable.__identifier__,
            self.get_catalog_indexdata(subfolder).get("object_provides"),
        )

    def test_cannot_restore_content_when_not_trashed(self):

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )

        with self.assertRaises(NotRestorable):
            Trasher(folder).restore()

    def test_cannot_restore_content_when_parent_is_trashed(self):

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        subfolder = api.content.create(
            container=folder, type="Folder", id="bar", title="Bar"
        )

        Trasher(folder).trash()

        with self.assertRaises(NotRestorable):
            Trasher(subfolder).restore()


    def test_cannot_restore_content_when_parent_was_trashed_earlier(self):
        
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        subfolder = api.content.create(
            container=folder, type="Folder", id="bar", title="Bar"
        )

        Trasher(subfolder).trash()
        Trasher(folder).trash()

        with self.assertRaises(NotRestorable):
            Trasher(subfolder).restore()

    def test_is_restorable_when_trashed(self):

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )

        self.assertFalse(Trasher(folder).is_restorable())

        Trasher(folder).trash()
        self.assertTrue(Trasher(folder).is_restorable())

    def test_not_restorable_when_parent_is_trashed_too(self):

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        subfolder = api.content.create(
            container=folder, type="Folder", id="bar", title="Bar"
        )

        self.assertFalse(Trasher(folder).is_restorable())
        self.assertFalse(Trasher(subfolder).is_restorable())

        Trasher(subfolder).trash()
        self.assertFalse(Trasher(folder).is_restorable())
        self.assertTrue(Trasher(subfolder).is_restorable())

        Trasher(folder).trash()
        self.assertTrue(Trasher(folder).is_restorable())
        self.assertFalse(Trasher(subfolder).is_restorable())


    def test_trashing_and_restoring_parent_of_a_trashed_content_does_not_influence_child(
        self,
    ):
        """
        Given a subpage is trashed.
        When the parent page is also trashed, and later restored, the subpage should still
        be trashed.
        The subpage should also stay restorable.
        """
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        bar = api.content.create(
            container=folder, type="Folder", id="bar", title="Bar"
        )

        self.assert_provides(folder, None)
        self.assert_provides(bar, None)

        Trasher(folder).trash()
        self.assert_provides(folder, ITrashed, IRestorable)
        self.assert_provides(bar, ITrashed)

        Trasher(folder).restore()
        self.assert_provides(folder, None)
        self.assert_provides(bar, None)

    def test_is_restorable_respectsIIsRestoreAllowedAdapter(self):
        response = {"allowed": True, "called": 0}

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )

        Trasher(folder).trash()

        @implementer(IIsRestoreAllowedAdapter)
        @adapter(Interface, Interface)
        def is_restore_allowed(context, request):
            response["called"] += 1
            return response["allowed"]

        getSiteManager().registerAdapter(is_restore_allowed)

        self.assertTrue(Trasher(folder).is_restorable())
        response["allowed"] = False
        self.assertFalse(Trasher(folder).is_restorable())
        self.assertEqual(2, response["called"])

    def test_events_are_fired(self):

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
        
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        
        fired_events = []
        registerHandler = self.portal.getSiteManager().registerHandler

        @registerHandler
        @adapter(Interface, IBeforeObjectTrashedEvent)
        def before_trashing(object, event):
            self.assertEqual(folder, object)
            self.assertEqual(folder, event.object)
            self.assertFalse(ITrashed.providedBy(object))
            fired_events.append(type(event).__name__)

        @registerHandler
        @adapter(Interface, IObjectTrashedEvent)
        def after_trashing(object, event):
            self.assertEqual(folder, object)
            self.assertEqual(folder, event.object)
            self.assertTrue(ITrashed.providedBy(object))
            fired_events.append(type(event).__name__)

        @registerHandler
        @adapter(Interface, IBeforeObjectRestoredEvent)
        def before_restoring(object, event):
            self.assertEqual(folder, object)
            self.assertEqual(folder, event.object)
            self.assertTrue(ITrashed.providedBy(object))
            fired_events.append(type(event).__name__)

        @registerHandler
        @adapter(Interface, IObjectRestoredEvent)
        def after_restoring(object, event):
            self.assertEqual(folder, object)
            self.assertEqual(folder, event.object)
            self.assertFalse(ITrashed.providedBy(object))
            fired_events.append(type(event).__name__)

        Trasher(folder).trash()
        self.assertEquals(
            ["BeforeObjectTrashedEvent", "ObjectTrashedEvent"], fired_events
        )
        fired_events[:] = []
        Trasher(folder).restore()
        self.assertEquals(
            ["BeforeObjectRestoredEvent", "ObjectRestoredEvent"], fired_events
        )


class TestDefaultIsRestoreAllowedAdapter(unittest.TestCase):
    layer = FTW_TRASH_FUNCTIONAL_TESTING
        
    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
    
    def test_requires_add_permission_on_parent(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        parent = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        child = api.content.create(
            container=parent, type="Folder", id="bar", title="Bar"
        )

        parent.manage_permission("Add portal content", roles=[], acquire=False)
        self.assertFalse(
            getMultiAdapter((child, self), IIsRestoreAllowedAdapter)
        )

        parent.manage_permission(
            "Add portal content", roles=["Contributor"], acquire=False
        )
        self.assertTrue(
            getMultiAdapter((child, self), IIsRestoreAllowedAdapter)
        )
