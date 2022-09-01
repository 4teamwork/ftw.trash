# # -*- coding: utf-8 -*-
# """Setup tests for this package."""
# from ftw.trash.testing import FTW_TRASH_INTEGRATION_TESTING  # noqa: E501
# from plone import api
# from plone.app.testing import TEST_USER_ID, setRoles
# import unittest

# try:
#     from Products.CMFPlone.utils import get_installer
# except ImportError:
#     get_installer = None


# class TestSetup(unittest.TestCase):
#     """Test that ftw.trash is properly installed."""

#     layer = FTW_TRASH_INTEGRATION_TESTING

#     def setUp(self):
#         """Custom shared utility setup for tests."""
#         self.portal = self.layer["portal"]
#         if get_installer:
#             self.installer = get_installer(self.portal, self.layer["request"])
#         else:
#             self.installer = api.portal.get_tool("portal_quickinstaller")

#     def test_product_installed(self):
#         """Test if ftw.trash is installed."""
#         self.assertTrue(self.installer.is_product_installed("ftw.trash"))

#     def test_browserlayer(self):
#         """Test that IFtwTrashLayer is registered."""
#         from plone.browserlayer import utils

#         from ftw.trash.interfaces import IFtwTrashLayer

#         self.assertIn(IFtwTrashLayer, utils.registered_layers())


# class TestUninstall(unittest.TestCase):

#     layer = FTW_TRASH_INTEGRATION_TESTING

#     def setUp(self):
#         self.portal = self.layer["portal"]
#         if get_installer:
#             self.installer = get_installer(self.portal, self.layer["request"])
#         else:
#             self.installer = api.portal.get_tool("portal_quickinstaller")
#         roles_before = api.user.get_roles(TEST_USER_ID)
#         setRoles(self.portal, TEST_USER_ID, ["Manager"])
#         self.installer.uninstall_product("ftw.trash")
#         setRoles(self.portal, TEST_USER_ID, roles_before)

#     def test_product_uninstalled(self):
#         """Test if ftw.trash is cleanly uninstalled."""
#         self.assertFalse(self.installer.is_product_installed("ftw.trash"))

#     def test_browserlayer_removed(self):
#         """Test that IFtwTrashLayer is removed."""
#         from plone.browserlayer import utils

#         from ftw.trash.interfaces import IFtwTrashLayer

#         self.assertNotIn(IFtwTrashLayer, utils.registered_layers())
