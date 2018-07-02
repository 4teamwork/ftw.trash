from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from ftw.trash.testing import TRASH_NOT_INSTALLED_FUNCTIONAL
from ftw.trash.tests import FunctionalTestCase
from Products.CMFCore.utils import getToolByName


class TestDeletion(FunctionalTestCase):
    layer = TRASH_NOT_INSTALLED_FUNCTIONAL

    @browsing
    def test_content_is_deleted_when_trash_not_installed(self, browser):
        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        self.grant('Manager')

        folder = create(Builder('folder').within(create(Builder('folder'))))
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(2, len(catalog.unrestrictedSearchResults()))

        browser.login().visit(folder)
        browser.click_on('Delete')
        self.assertEquals('Do you really want to delete this folder and all its contents?',
                          plone.first_heading())
        browser.click_on('Delete')
        self.assertNotIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(1, len(catalog.unrestrictedSearchResults()))

    @browsing
    def test_site_root_content_is_deleted_when_trash_not_installed(self, browser):
        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        self.grant('Manager')

        folder = create(Builder('folder'))
        self.assertIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(1, len(catalog.unrestrictedSearchResults()))

        browser.login().visit(folder)
        browser.click_on('Delete')
        self.assertEquals('Do you really want to delete this folder and all its contents?',
                          plone.first_heading())
        browser.click_on('Delete')
        self.assertNotIn(folder.getId(), aq_parent(aq_inner(folder)).objectIds())
        self.assertEqual(0, len(catalog.unrestrictedSearchResults()))
