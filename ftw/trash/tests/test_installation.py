from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


PLONE_FUNCTIONAL  = FunctionalTesting(
    bases=(PLONE_FIXTURE,
           BUILDER_LAYER,
           set_builder_session_factory(functional_session_factory)),
    name='Plone:Functional:biulder')


class TestTrashNotInstalled(TestCase):
    layer = PLONE_FUNCTIONAL

    @browsing
    def test_content_is_deleted_when_trash_not_installed(self, browser):
        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        setRoles(self.layer['portal'], TEST_USER_ID, ['Contributor', 'Editor'])

        page = create(Builder('page'))
        self.assertIn(page.getId(), aq_parent(aq_inner(page)).objectIds())
        self.assertEqual(1, len(catalog.unrestrictedSearchResults()))

        browser.login().visit(page)
        browser.click_on('Delete')
        self.assertEqual('Do you really want to delete this item?', plone.first_heading())
        browser.click_on('Delete')
        self.assertNotIn(page.getId(), aq_parent(aq_inner(page)).objectIds())
        self.assertEqual(0, len(catalog.unrestrictedSearchResults()))
