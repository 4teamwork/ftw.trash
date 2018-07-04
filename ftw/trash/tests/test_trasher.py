from ftw.builder import Builder
from ftw.builder import create
from ftw.trash.exceptions import NotRestorable
from ftw.trash.interfaces import IRestorable
from ftw.trash.interfaces import ITrashed
from ftw.trash.tests import duplicate_with_dexterity
from ftw.trash.tests import FunctionalTestCase
from ftw.trash.trasher import Trasher
from zExceptions import Unauthorized


@duplicate_with_dexterity
class TestTrasher(FunctionalTestCase):

    def test_marks_trashed_page_as_trashed_and_restorable(self):
        self.grant('Contributor')

        folder = create(Builder('folder'))
        self.assertFalse(ITrashed.providedBy(folder))
        self.assertFalse(IRestorable.providedBy(folder))

        Trasher(folder).trash()
        self.assertTrue(ITrashed.providedBy(folder))
        self.assertTrue(IRestorable.providedBy(folder))

    def test_marks_children_of_trashed_folder_only_as_trashed(self):
        self.grant('Contributor')

        folder = create(Builder('folder'))
        subfolder = create(Builder('folder').within(folder))
        self.assertFalse(ITrashed.providedBy(folder))
        self.assertFalse(IRestorable.providedBy(folder))
        self.assertFalse(ITrashed.providedBy(subfolder))
        self.assertFalse(IRestorable.providedBy(subfolder))

        Trasher(folder).trash()
        self.assertTrue(ITrashed.providedBy(folder))
        self.assertTrue(IRestorable.providedBy(folder))
        self.assertTrue(ITrashed.providedBy(subfolder))
        self.assertFalse(IRestorable.providedBy(subfolder))

    def test_catalog_is_updated_when_trashing_content(self):
        self.grant('Contributor')

        folder = create(Builder('folder'))
        subfolder = create(Builder('folder').within(folder))

        self.assertFalse(self.get_catalog_indexdata(folder).get('trashed'))
        self.assertNotIn(ITrashed.__identifier__,
                         self.get_catalog_indexdata(folder).get('object_provides'))
        self.assertNotIn(IRestorable.__identifier__,
                         self.get_catalog_indexdata(folder).get('object_provides'))

        self.assertFalse(self.get_catalog_indexdata(subfolder).get('trashed'))
        self.assertNotIn(ITrashed.__identifier__,
                         self.get_catalog_indexdata(subfolder).get('object_provides'))
        self.assertNotIn(IRestorable.__identifier__,
                         self.get_catalog_indexdata(subfolder).get('object_provides'))

        Trasher(folder).trash()
        self.assertTrue(self.get_catalog_indexdata(folder).get('trashed'))
        self.assertIn(ITrashed.__identifier__,
                      self.get_catalog_indexdata(folder).get('object_provides'))
        self.assertIn(IRestorable.__identifier__,
                      self.get_catalog_indexdata(folder).get('object_provides'))

        self.assertTrue(self.get_catalog_indexdata(subfolder).get('trashed'))
        self.assertIn(ITrashed.__identifier__,
                      self.get_catalog_indexdata(subfolder).get('object_provides'))
        self.assertNotIn(IRestorable.__identifier__,
                         self.get_catalog_indexdata(subfolder).get('object_provides'))

    def test_restorable_content_can_be_restored(self):
        self.grant('Site Administrator')

        folder = create(Builder('folder'))
        self.assertFalse(ITrashed.providedBy(folder))
        self.assertFalse(IRestorable.providedBy(folder))

        Trasher(folder).trash()
        self.assertTrue(ITrashed.providedBy(folder))
        self.assertTrue(IRestorable.providedBy(folder))

        Trasher(folder).restore()
        self.assertFalse(ITrashed.providedBy(folder))
        self.assertFalse(IRestorable.providedBy(folder))

    def test_children_are_restored_correctly(self):
        self.grant('Site Administrator')

        folder = create(Builder('folder'))
        subfolder = create(Builder('folder').within(folder))
        self.assertFalse(ITrashed.providedBy(folder))
        self.assertFalse(IRestorable.providedBy(folder))
        self.assertFalse(ITrashed.providedBy(subfolder))
        self.assertFalse(IRestorable.providedBy(subfolder))

        Trasher(folder).trash()
        self.assertTrue(ITrashed.providedBy(folder))
        self.assertTrue(IRestorable.providedBy(folder))
        self.assertTrue(ITrashed.providedBy(subfolder))
        self.assertFalse(IRestorable.providedBy(subfolder))

        Trasher(folder).restore()
        self.assertFalse(ITrashed.providedBy(folder))
        self.assertFalse(IRestorable.providedBy(folder))
        self.assertFalse(ITrashed.providedBy(subfolder))
        self.assertFalse(IRestorable.providedBy(subfolder))

    def test_catalog_is_updated_when_restoring_content(self):
        self.grant('Site Administrator')

        folder = create(Builder('folder'))
        subfolder = create(Builder('folder').within(folder))

        self.assertFalse(self.get_catalog_indexdata(folder).get('trashed'))
        self.assertNotIn(ITrashed.__identifier__,
                         self.get_catalog_indexdata(folder).get('object_provides'))
        self.assertNotIn(IRestorable.__identifier__,
                         self.get_catalog_indexdata(folder).get('object_provides'))

        self.assertFalse(self.get_catalog_indexdata(subfolder).get('trashed'))
        self.assertNotIn(ITrashed.__identifier__,
                         self.get_catalog_indexdata(subfolder).get('object_provides'))
        self.assertNotIn(IRestorable.__identifier__,
                         self.get_catalog_indexdata(subfolder).get('object_provides'))

        Trasher(folder).trash()
        self.assertTrue(self.get_catalog_indexdata(folder).get('trashed'))
        self.assertIn(ITrashed.__identifier__,
                      self.get_catalog_indexdata(folder).get('object_provides'))
        self.assertIn(IRestorable.__identifier__,
                      self.get_catalog_indexdata(folder).get('object_provides'))

        self.assertTrue(self.get_catalog_indexdata(subfolder).get('trashed'))
        self.assertIn(ITrashed.__identifier__,
                      self.get_catalog_indexdata(subfolder).get('object_provides'))
        self.assertNotIn(IRestorable.__identifier__,
                         self.get_catalog_indexdata(subfolder).get('object_provides'))

        Trasher(folder).restore()
        self.assertFalse(self.get_catalog_indexdata(folder).get('trashed'))
        self.assertNotIn(ITrashed.__identifier__,
                         self.get_catalog_indexdata(folder).get('object_provides'))
        self.assertNotIn(IRestorable.__identifier__,
                         self.get_catalog_indexdata(folder).get('object_provides'))

        self.assertFalse(self.get_catalog_indexdata(subfolder).get('trashed'))
        self.assertNotIn(ITrashed.__identifier__,
                         self.get_catalog_indexdata(subfolder).get('object_provides'))
        self.assertNotIn(IRestorable.__identifier__,
                         self.get_catalog_indexdata(subfolder).get('object_provides'))

    def test_cannot_restore_content_when_not_trashed(self):
        self.grant('Site Administrator')

        folder = create(Builder('folder'))

        with self.assertRaises(NotRestorable):
            Trasher(folder).restore()

    def test_cannot_restore_content_when_parent_is_trashed(self):
        self.grant('Site Administrator')

        folder = create(Builder('folder'))
        subfolder = create(Builder('folder').within(folder))
        Trasher(folder).trash()

        with self.assertRaises(NotRestorable):
            Trasher(subfolder).restore()

    def test_restore_requires_permission(self):
        self.grant('Contributor')

        parent = create(Builder('folder'))
        parent.manage_permission('Restore trashed content', roles=[], acquire=False)

        folder = create(Builder('folder').within(parent))
        Trasher(folder).trash()
        self.assertTrue(ITrashed.providedBy(folder))

        with self.assertRaises(Unauthorized):
            Trasher(folder).restore()

        self.assertTrue(ITrashed.providedBy(folder))

        parent.manage_permission('Restore trashed content', roles=['Contributor'], acquire=False)
        Trasher(folder).restore()
        self.assertFalse(ITrashed.providedBy(folder))
