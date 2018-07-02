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

        page = create(Builder('page').within(create(Builder('folder'))))
        self.assertIn(page.getId(), aq_parent(aq_inner(page)).objectIds())
        self.assertEqual(2, len(catalog.unrestrictedSearchResults()))

        browser.login().visit(page)
        browser.click_on('Delete')
        self.assertEqual('Do you really want to delete this item?', plone.first_heading())
        browser.click_on('Delete')
        self.assertNotIn(page.getId(), aq_parent(aq_inner(page)).objectIds())
        self.assertEqual(1, len(catalog.unrestrictedSearchResults()))

    @browsing
    def test_site_root_content_is_deleted_when_trash_not_installed(self, browser):
        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        self.grant('Manager')

        page = create(Builder('page'))
        self.assertIn(page.getId(), aq_parent(aq_inner(page)).objectIds())
        self.assertEqual(1, len(catalog.unrestrictedSearchResults()))

        browser.login().visit(page)
        browser.click_on('Delete')
        self.assertEqual('Do you really want to delete this item?', plone.first_heading())
        browser.click_on('Delete')
        self.assertNotIn(page.getId(), aq_parent(aq_inner(page)).objectIds())
        self.assertEqual(0, len(catalog.unrestrictedSearchResults()))
