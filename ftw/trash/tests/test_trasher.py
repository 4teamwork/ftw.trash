from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from ftw.trash.exceptions import NotRestorable
from ftw.trash.interfaces import IBeforeObjectRestoredEvent
from ftw.trash.interfaces import IBeforeObjectTrashedEvent
from ftw.trash.interfaces import IIsRestoreAllowedAdapter
from ftw.trash.interfaces import IObjectRestoredEvent
from ftw.trash.interfaces import IObjectTrashedEvent
from ftw.trash.interfaces import IRestorable
from ftw.trash.interfaces import ITrashed
from ftw.trash.tests import duplicate_with_dexterity
from ftw.trash.tests import FunctionalTestCase
from ftw.trash.trasher import Trasher
from zExceptions import Unauthorized
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.interface import implementer
from zope.interface import Interface


@duplicate_with_dexterity
class TestTrasher(FunctionalTestCase):

    def test_marks_trashed_page_as_trashed_and_restorable(self):
        self.grant('Contributor')

        folder = create(Builder('folder'))
        self.assert_provides(folder, None)

        Trasher(folder).trash()
        self.assert_provides(folder, IRestorable, ITrashed)

    def test_marks_children_of_trashed_folder_only_as_trashed(self):
        self.grant('Contributor')

        folder = create(Builder('folder'))
        subfolder = create(Builder('folder').within(folder))
        self.assert_provides(folder, None)
        self.assert_provides(subfolder, None)

        Trasher(folder).trash()
        self.assert_provides(folder, IRestorable, ITrashed)
        self.assert_provides(subfolder, ITrashed)

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
        self.assert_provides(folder, None)

        Trasher(folder).trash()
        self.assert_provides(folder, IRestorable, ITrashed)

        Trasher(folder).restore()
        self.assert_provides(folder, None)

    def test_children_are_restored_correctly(self):
        self.grant('Site Administrator')

        folder = create(Builder('folder'))
        subfolder = create(Builder('folder').within(folder))
        self.assert_provides(folder, None)
        self.assert_provides(subfolder, None)

        Trasher(folder).trash()
        self.assert_provides(folder, IRestorable, ITrashed)
        self.assert_provides(subfolder, ITrashed)

        Trasher(folder).restore()
        self.assert_provides(folder, None)
        self.assert_provides(subfolder, None)

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

    def test_cannot_restore_content_when_parent_was_trashed_earlier(self):
        self.grant('Site Administrator')

        folder = create(Builder('folder'))
        subfolder = create(Builder('folder').within(folder))
        Trasher(subfolder).trash()
        Trasher(folder).trash()

        with self.assertRaises(NotRestorable):
            Trasher(subfolder).restore()

    def test_restore_requires_permission(self):
        self.grant('Contributor')

        parent = create(Builder('folder'))
        parent.manage_permission('Restore trashed content', roles=[], acquire=False)

        folder = create(Builder('folder').within(parent))
        Trasher(folder).trash()
        self.assert_provides(folder, IRestorable, ITrashed)

        with self.assertRaises(Unauthorized):
            Trasher(folder).restore()

        self.assert_provides(folder, IRestorable, ITrashed)

        parent.manage_permission('Restore trashed content', roles=['Contributor'], acquire=False)
        Trasher(folder).restore()
        self.assert_provides(folder, None)

    def test_is_restorable_when_trashed(self):
        self.grant('Site Administrator')

        folder = create(Builder('folder'))
        self.assertFalse(Trasher(folder).is_restorable())

        Trasher(folder).trash()
        self.assertTrue(Trasher(folder).is_restorable())

    def test_not_restorable_when_parent_is_trashed_too(self):
        self.grant('Site Administrator')

        folder = create(Builder('folder'))
        subfolder = create(Builder('folder').within(folder))
        self.assertFalse(Trasher(folder).is_restorable())
        self.assertFalse(Trasher(subfolder).is_restorable())

        Trasher(subfolder).trash()
        self.assertFalse(Trasher(folder).is_restorable())
        self.assertTrue(Trasher(subfolder).is_restorable())

        Trasher(folder).trash()
        self.assertTrue(Trasher(folder).is_restorable())
        self.assertFalse(Trasher(subfolder).is_restorable())

    def test_trashing_and_restoring_updates_modified_date(self):
        self.grant('Site Administrator')

        created = datetime(2011, 1, 1, 1, 1, 1)
        trashed = datetime(2022, 2, 2, 2, 2, 2)
        restored = datetime(2033, 3, 3, 3, 3, 3)

        with freeze(created):
            folder = create(Builder('folder'))
            subfolder = create(Builder('folder').within(folder))

        self.assert_modified_date(created, folder)
        self.assert_modified_date(created, subfolder)

        with freeze(trashed):
            Trasher(folder).trash()

        self.assert_modified_date(trashed, folder)
        self.assert_modified_date(trashed, subfolder)

        with freeze(restored):
            Trasher(folder).restore()

        self.assert_modified_date(restored, folder)
        self.assert_modified_date(restored, subfolder)

    def test_trashing_and_restoring_parent_of_a_trashed_content_does_not_influence_child(self):
        """
        Given a subpage is trashed.
        When the parent page is also trashed, and later restored, the subpage should still
        be trashed.
        The subpage should also stay restorable.
        """
        self.grant('Site Administrator')

        folder = create(Builder('folder'))
        foo = create(Builder('folder').within(folder))
        bar = create(Builder('folder').within(folder))

        self.assert_provides(folder, None)
        self.assert_provides(foo, None)
        self.assert_provides(bar, None)

        Trasher(foo).trash()
        self.assert_provides(folder, None)
        self.assert_provides(foo, ITrashed, IRestorable)
        self.assert_provides(bar, None)

        Trasher(folder).trash()
        self.assert_provides(folder, ITrashed, IRestorable)
        self.assert_provides(foo, ITrashed, IRestorable)
        self.assert_provides(bar, ITrashed)

        Trasher(folder).restore()
        self.assert_provides(folder, None)
        self.assert_provides(foo, ITrashed, IRestorable)
        self.assert_provides(bar, None)

    def test_is_restorable_respectsIIsRestoreAllowedAdapter(self):
        response = {'allowed': True, 'called': 0}
        self.grant('Site Administrator')

        folder = create(Builder('folder'))
        Trasher(folder).trash()

        @implementer(IIsRestoreAllowedAdapter)
        @adapter(Interface, Interface)
        def is_restore_allowed(context, request):
            response['called'] += 1
            return response['allowed']

        getSiteManager().registerAdapter(is_restore_allowed)

        self.assertTrue(Trasher(folder).is_restorable())
        response['allowed'] = False
        self.assertFalse(Trasher(folder).is_restorable())
        self.assertEqual(2, response['called'])

    def test_events_are_fired(self):
        self.grant('Site Administrator')
        folder = create(Builder('folder'))
        fired_events = []
        registerHandler = self.portal.getSiteManager().registerHandler

        @registerHandler
        @adapter(Interface, IBeforeObjectTrashedEvent)
        def before_trashing(object, event):
            self.assertEqual(folder, object)
            self.assertEqual(folder, event.object)
            self.assertFalse(ITrashed.providedBy(object))
            fired_events.append(type(event).__name__)

        @registerHandler
        @adapter(Interface, IObjectTrashedEvent)
        def after_trashing(object, event):
            self.assertEqual(folder, object)
            self.assertEqual(folder, event.object)
            self.assertTrue(ITrashed.providedBy(object))
            fired_events.append(type(event).__name__)

        @registerHandler
        @adapter(Interface, IBeforeObjectRestoredEvent)
        def before_restoring(object, event):
            self.assertEqual(folder, object)
            self.assertEqual(folder, event.object)
            self.assertTrue(ITrashed.providedBy(object))
            fired_events.append(type(event).__name__)

        @registerHandler
        @adapter(Interface, IObjectRestoredEvent)
        def after_restoring(object, event):
            self.assertEqual(folder, object)
            self.assertEqual(folder, event.object)
            self.assertFalse(ITrashed.providedBy(object))
            fired_events.append(type(event).__name__)

        Trasher(folder).trash()
        self.assertEquals(['BeforeObjectTrashedEvent', 'ObjectTrashedEvent'], fired_events)
        fired_events[:] = []
        Trasher(folder).restore()
        self.assertEquals(['BeforeObjectRestoredEvent', 'ObjectRestoredEvent'], fired_events)


@duplicate_with_dexterity
class TestDefaultIsRestoreAllowedAdapter(FunctionalTestCase):

    def test_requires_add_permission_on_parent(self):
        self.grant('Contributor')
        parent = create(Builder('folder'))
        child = create(Builder('folder').within(parent))

        parent.manage_permission('Add portal content', roles=[], acquire=False)
        self.assertFalse(
            getMultiAdapter((child, self.request), IIsRestoreAllowedAdapter))

        parent.manage_permission('Add portal content', roles=['Contributor'], acquire=False)
        self.assertTrue(
            getMultiAdapter((child, self.request), IIsRestoreAllowedAdapter))
