from ftw.builder import Builder
from ftw.builder import create
from ftw.trash.interfaces import IRestorable
from ftw.trash.interfaces import ITrashed
from ftw.trash.tests import duplicate_with_dexterity
from ftw.trash.tests import FunctionalTestCase
from ftw.trash.trasher import Trasher


@duplicate_with_dexterity
class TestTrasher(FunctionalTestCase):

    def test_marks_trashed_pageect_as_trashed_and_restorable(self):
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

        self.assertNotIn(ITrashed.__identifier__,
                         self.get_catalog_indexdata(folder).get('object_provides'))
        self.assertNotIn(IRestorable.__identifier__,
                         self.get_catalog_indexdata(folder).get('object_provides'))
        self.assertNotIn(ITrashed.__identifier__,
                         self.get_catalog_indexdata(subfolder).get('object_provides'))
        self.assertNotIn(IRestorable.__identifier__,
                         self.get_catalog_indexdata(subfolder).get('object_provides'))

        Trasher(folder).trash()
        self.assertIn(ITrashed.__identifier__,
                      self.get_catalog_indexdata(folder).get('object_provides'))
        self.assertIn(IRestorable.__identifier__,
                      self.get_catalog_indexdata(folder).get('object_provides'))
        self.assertIn(ITrashed.__identifier__,
                      self.get_catalog_indexdata(subfolder).get('object_provides'))
        self.assertNotIn(IRestorable.__identifier__,
                         self.get_catalog_indexdata(subfolder).get('object_provides'))
