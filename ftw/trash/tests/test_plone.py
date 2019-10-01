from ftw.builder import Builder
from ftw.builder import create
from ftw.trash.tests import duplicate_with_dexterity
from ftw.trash.tests import FunctionalTestCase
from ftw.trash.trasher import Trasher


@duplicate_with_dexterity
class TestPloneIntegration(FunctionalTestCase):

    def test_folder_objectItems_returns_trashed_content(self):
        """A folder's objectItems should return trashed content.
        """
        self.grant('Contributor')
        container = create(Builder('folder').titled(u'Container'))
        foo = create(Builder('folder').titled(u'Foo').within(container))
        bar = create(Builder('folder').titled(u'Bar').within(container))
        self.assertEqual([('foo', foo), ('bar', bar)], list(container.objectItems()))
        Trasher(foo).trash()
        self.assertEqual([('foo', foo), ('bar', bar)], list(container.objectItems()))

    def test_plone_objectItems_returns_trashed_content(self):
        """A Plone site's objectItems should return trashed content.
        """
        self.grant('Contributor')
        foo = create(Builder('folder').titled(u'Foo'))
        self.assertIn(('foo', foo), list(self.portal.objectItems()))
        Trasher(foo).trash()
        self.assertIn(('foo', foo), list(self.portal.objectItems()))

    def test_folder_contentItems_does_not_return_trashed_content(self):
        """A folder's contentItems should not return trashed content.
        """
        self.grant('Contributor')
        container = create(Builder('folder').titled(u'Container'))
        foo = create(Builder('folder').titled(u'Foo').within(container))
        bar = create(Builder('folder').titled(u'Bar').within(container))
        self.assertEqual([('foo', foo), ('bar', bar)], container.contentItems())
        Trasher(foo).trash()
        self.assertEqual([('bar', bar)], container.contentItems())

    def test_plone_contentItems_does_not_return_trashed_content(self):
        """A Plone site's contentItems should not return trashed content.
        """
        self.grant('Contributor')
        foo = create(Builder('folder').titled(u'Foo'))
        self.assertIn(('foo', foo), self.portal.contentItems())
        Trasher(foo).trash()
        self.assertNotIn(('foo', foo), self.portal.contentItems())

    def test_listFolderContents_does_not_return_trashed_content(self):
        """A folder's listFolderContents should not return trashed content.
        """
        self.grant('Contributor')
        container = create(Builder('folder').titled(u'Container'))
        foo = create(Builder('folder').titled(u'Foo').within(container))
        bar = create(Builder('folder').titled(u'Bar').within(container))
        self.assertEqual([foo, bar], container.listFolderContents())
        Trasher(foo).trash()
        self.assertEqual([bar], container.listFolderContents())

    def test_getFolderContents_does_not_return_trashed_content(self):
        """A folder's getFolderContents should not return trashed content.
        """
        self.grant('Contributor')
        container = create(Builder('folder').titled(u'Container'))
        foo = create(Builder('folder').titled(u'Foo').within(container))
        bar = create(Builder('folder').titled(u'Bar').within(container))
        self.assertEqual(
            [foo, bar],
            [brain.getObject() for brain in container.getFolderContents()])
        Trasher(foo).trash()
        self.assertEqual(
            [bar],
            [brain.getObject() for brain in container.getFolderContents()])
