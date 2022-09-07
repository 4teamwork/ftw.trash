from ftw.trash.testing import FTW_TRASH_FUNCTIONAL_TESTING
from ftw.trash.trasher import Trasher
from ftw.trash.interfaces import (
    IRestorable,
    ITrashed,
)

from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.testing import TEST_USER_ID, setRoles

import unittest



class TestTrashNotInstalled(unittest.TestCase):
    layer = FTW_TRASH_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]

    def assert_provides(self, obj, *expected):
        expected = set([_f for _f in expected if _f])
        got = {iface for iface in (IRestorable, ITrashed) if iface.providedBy(obj)}
        self.assertEquals(
            expected, got, "Unexpected interfaces provided by {!r}".format(obj)
        )


    def test_content_is_deleted_when_trash_not_installed(self):

        catalog = getToolByName(self.layer["portal"], "portal_catalog")
        
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        folder1 = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )        
        folder2 = api.content.create(
            container=folder1,
            type="Folder",
            id="bar",
            title="Bar",
        )
        self.assertIn(folder2.id, folder1.objectIds())

        Trasher(folder2).trash()
        self.assertIn(folder2.id, folder1.objectIds())


    def test_manage_delObjects_requires_both_delete_permissions(self):
        '''Test already present in ftw.trash.tests.test_deletion'''
