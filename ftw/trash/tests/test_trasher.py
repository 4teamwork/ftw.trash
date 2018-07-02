from ftw.builder import Builder
from ftw.builder import create
from ftw.trash.interfaces import IRestorable
from ftw.trash.interfaces import ITrashed
from ftw.trash.tests import FunctionalTestCase
from ftw.trash.trasher import Trasher


class TestTrasher(FunctionalTestCase):

    def test_marks_trashed_pageect_as_trashed_and_restorable(self):
        self.grant('Contributor')

        page = create(Builder('page'))
        self.assertFalse(ITrashed.providedBy(page))
        self.assertFalse(IRestorable.providedBy(page))

        Trasher(page).trash()
        self.assertTrue(ITrashed.providedBy(page))
        self.assertTrue(IRestorable.providedBy(page))

    def test_marks_children_of_trashed_folder_only_as_trashed(self):
        self.grant('Contributor')

        folder = create(Builder('folder'))
        page = create(Builder('page').within(folder))
        self.assertFalse(ITrashed.providedBy(folder))
        self.assertFalse(IRestorable.providedBy(folder))
        self.assertFalse(ITrashed.providedBy(page))
        self.assertFalse(IRestorable.providedBy(page))

        Trasher(folder).trash()
        self.assertTrue(ITrashed.providedBy(folder))
        self.assertTrue(IRestorable.providedBy(folder))
        self.assertTrue(ITrashed.providedBy(page))
        self.assertFalse(IRestorable.providedBy(page))
