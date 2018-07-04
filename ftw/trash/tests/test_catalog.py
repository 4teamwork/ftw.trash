from ftw.builder import Builder
from ftw.builder import create
from ftw.trash.tests import duplicate_with_dexterity
from ftw.trash.tests import FunctionalTestCase
from ftw.trash.trasher import Trasher
from Products.CMFCore.utils import getToolByName


@duplicate_with_dexterity
class TestCatalog(FunctionalTestCase):

    def test_filters_trashed_content_by_default(self):
        self.grant('Contributor')

        create(Builder('folder').titled(u'Foo'))
        bar = create(Builder('folder').titled(u'Bar'))
        self.assert_catalog_result({'Bar', 'Foo'})

        Trasher(bar).trash()
        self.assert_catalog_result({'Foo'})

    def test_returns_trashed_content_when_explicitly_queried_for(self):
        self.grant('Contributor')

        create(Builder('folder').titled(u'Foo'))
        Trasher(create(Builder('folder').titled(u'Bar'))).trash()
        self.assert_catalog_result({'Foo'}, query={})
        self.assert_catalog_result({'Foo', 'Bar'}, query={'trashed': None})
        self.assert_catalog_result({'Bar'}, query={'trashed': True})
        self.assert_catalog_result({'Foo'}, query={'trashed': False})

    def test_unrestrictedSearchResults_returns_all_items_by_default(self):
        """unrestrictedSearchResults must return all items by default, no matter whether
        they're trashed or not, because ftw.upgrade uses unrestrictedSearchResults
        and we want to make sure that all objects are migrated.
        """
        self.grant('Contributor')

        create(Builder('folder').titled(u'Foo'))
        Trasher(create(Builder('folder').titled(u'Bar'))).trash()
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.assertItemsEqual(('Foo', 'Bar'),
                              [brain.Title for brain in catalog.unrestrictedSearchResults()])

    def assert_catalog_result(self, expected_titles, query={}):
        catalog = getToolByName(self.portal, 'portal_catalog')
        got_titles1 = [brain.Title for brain in catalog.searchResults(**query)]
        got_titles2 = [brain.Title for brain in catalog(**query)]

        self.assertItemsEqual(
            got_titles1, got_titles2,
            'portal_catalog({!r}) != portal_catalog.searchResults({!r})'.format(query, query))

        self.assertItemsEqual(expected_titles, got_titles1)
