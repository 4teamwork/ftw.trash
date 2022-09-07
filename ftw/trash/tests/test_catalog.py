# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from ftw.trash.testing import FTW_TRASH_INTEGRATION_TESTING  # noqa: E501
from ftw.trash.trasher import Trasher

from plone import api
from plone.app.testing import TEST_USER_ID, setRoles
import unittest

try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestCatalog(unittest.TestCase):
    layer = FTW_TRASH_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_filters_trashed_content_by_default(self):

        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        
        foo = api.content.create(
            container=self.portal,
            type="Document",
            id="foo",
            title="Foo",
        )

        self.assertEqual(foo.Title(), "Foo")

        parent = foo.__parent__
        self.assertIn("foo", parent.objectIds())

        bar = api.content.create(
            container=self.portal,
            type="Document",
            id="bar",
            title="Bar",
        )

        brains = api.content.find(id=["foo", "bar"])
        self.assertTrue(len(brains) == 2)

        Trasher(bar).trash()
    
        brains = api.content.find(id=["foo", "bar"])
        self.assertTrue(len(brains) == 1)
        self.assertEqual(brains[0].id, "foo")

    def test_returns_trashed_content_when_explicitly_queried_for(self):
        
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        api.content.create(
            container=self.portal,
            type="Document",
            id="foo",
            title="Foo",
        )
        bar = api.content.create(
            container=self.portal,
            type="Document",
            id="bar",
            title="Bar",
        )

        Trasher(bar).trash()

        brains = api.content.find(id="foo")
        self.assertTrue(len(brains) == 1)

        brains = api.content.find(id=["foo", "bar"], trashed=None)
        self.assertTrue(len(brains) == 2)

        brains = api.content.find(id=["foo", "bar"], trashed=True)
        self.assertTrue(len(brains) == 1)

        brains = api.content.find(id=["foo", "bar"], trashed=False)
        self.assertTrue(len(brains) == 1)

    def test_unrestrictedSearchResults_returns_all_items_by_default(self):
        """unrestrictedSearchResults must return all items by default, no matter whether
        they're trashed or not, because ftw.upgrade uses unrestrictedSearchResults
        and we want to make sure that all objects are migrated.
        """
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        api.content.create(
            container=self.portal,
            type="Document",
            id="foo",
            title="Foo",
        )
        bar = api.content.create(
            container=self.portal,
            type="Document",
            id="bar",
            title="Bar",
        )

        Trasher(bar).trash()

        brains = api.content.find(id=["foo", "bar"])
        self.assertTrue(len(brains) == 1)

        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog.unrestrictedSearchResults(id=["foo", "bar"])
        self.assertTrue(len(brains) == 2)
