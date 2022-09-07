from ftw.trash.testing import FTW_TRASH_FUNCTIONAL_TESTING

from Products.CMFCore.utils import getToolByName
import unittest


class TestDefaultProfile(unittest.TestCase):
    layer = FTW_TRASH_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        
    def test_installed(self):
        portal_setup = getToolByName(self.portal, "portal_setup")
        version = portal_setup.getLastVersionForProfile("ftw.trash:default")
        self.assertNotEqual(version, None)
        self.assertNotEqual(version, "unknown")
