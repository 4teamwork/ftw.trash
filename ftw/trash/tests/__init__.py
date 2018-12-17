from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from contextlib import contextmanager
from DateTime import DateTime
from ftw.builder import builder_registry
from ftw.testing import IS_PLONE_5
from ftw.trash.interfaces import IRestorable
from ftw.trash.interfaces import ITrashed
from ftw.trash.testing import TRASH_FUNCTIONAL
from ftw.trash.tests.builders import DXFolderBuilder
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
import sys
import transaction


class FunctionalTestCase(TestCase):
    layer = TRASH_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()

    @contextmanager
    def user(self, username):
        if hasattr(username, 'getUserName'):
            username = username.getUserName()

        sm = getSecurityManager()
        login(self.layer['portal'], username)
        try:
            yield
        finally:
            setSecurityManager(sm)

    def get_catalog_indexdata(self, obj):
        """Return the catalog index data for an object as dict.
        """
        self.maybe_process_indexing_queue()
        catalog = getToolByName(self.portal, 'portal_catalog')
        rid = catalog.getrid('/'.join(obj.getPhysicalPath()))
        return catalog.getIndexDataForRID(rid)

    def get_catalog_metadata(self, obj):
        """Return the catalog metadata for an object as dict.
        """
        self.maybe_process_indexing_queue()
        catalog = getToolByName(self.portal, 'portal_catalog')
        rid = catalog.getrid('/'.join(obj.getPhysicalPath()))
        return catalog.getMetadataForRID(rid)

    def assert_modified_date(self, expected, obj):
        expected = DateTime(expected)
        self.assertEqual(expected, obj.modified(), '{!r}.modified() is wrong'.format(obj))
        self.assertEqual(expected, self.get_catalog_metadata(obj)['modified'],
                         '{!r}\'s "modified" metadata is wrong'.format(obj))

        catalog = getToolByName(self.portal, 'portal_catalog')
        modified_index = catalog._catalog.indexes.get('modified')

        self.assertEqual(
            modified_index._convert(expected), self.get_catalog_indexdata(obj)['modified'],
            '{!r}\'s "modified" index data is wrong'.format(obj))

    def assert_provides(self, obj, *expected):
        expected = set(filter(None, expected))
        got = {iface for iface in (IRestorable, ITrashed) if iface.providedBy(obj)}
        self.assertEquals(expected, got, 'Unexpected interfaces provided by {!r}'.format(obj))

    @property
    def is_dexterity(self):
        return IS_PLONE_5

    def maybe_process_indexing_queue(self):
        if not IS_PLONE_5:
            return

        from Products.CMFCore.indexing import processQueue
        processQueue()


def duplicate_with_dexterity(klass):
    """Decorator for duplicating a test suite to be ran against dexterity contents.

    The tests are ran against archetypes by default, meaning that we use the builder
    "folder" as AT builder for the FTI "Folder".
    When using the @duplicate_with_dexterity decorator, an additional class is registered
    (postfixed "Dexterity"), where the "folder" builder is changed to a DX builder
    creating the FTI "dxfolder", which is registered in a Generic Setup test-profile.

    So if you use this decorator, be aware, that only "Builder('folder')" is replaced
    with dexterity, all other builders and other code does not change.
    """

    if IS_PLONE_5:
        # The default types (Folder etc.) in Plone 5 are already Dexterity.
        # So we do not test Archetypes under Plone 5 anymore, thus we do not
        # need to duplicate the tests.
        return klass

    class DexterityTestSuite(klass):
        def setUp(self):
            self._builder_isolation = builder_registry.temporary_builder_config()
            self._builder_isolation.__enter__()
            builder_registry.register('folder', DXFolderBuilder, force=True)
            super(DexterityTestSuite, self).setUp()

        def tearDown(self):
            super(DexterityTestSuite, self).tearDown()
            self._builder_isolation.__exit__(None, None, None)
            del self._builder_isolation

        @property
        def is_dexterity(self):
            return True

    DexterityTestSuite.__name__ = klass.__name__ + 'Dexterity'
    DexterityTestSuite.__module__ = klass.__module__
    sys._getframe(1).f_locals[DexterityTestSuite.__name__] = DexterityTestSuite
    return klass
