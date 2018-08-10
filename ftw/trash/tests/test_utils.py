from ftw.trash.testing import TRASH_NOT_INSTALLED_FUNCTIONAL
from ftw.trash.tests import FunctionalTestCase
from ftw.trash.utils import filter_children_in_paths
from ftw.trash.utils import is_trash_profile_installed
from unittest2 import TestCase


class TestUtilsWhenInstalled(FunctionalTestCase):

    def test_is_trash_profile_installed(self):
        self.assertTrue(is_trash_profile_installed())


class TestUtilsWhenNotInstalled(FunctionalTestCase):
    layer = TRASH_NOT_INSTALLED_FUNCTIONAL

    def test_is_trash_profile_installed(self):
        self.assertFalse(is_trash_profile_installed())


class TestFilterChildrenInPaths(TestCase):

    def test(self):
        paths = ['/a/b/c/d', '/a', '/b', '/a/b/c/d/e/f', '/c/a/b/d', '/abab']
        self.assertEquals(['/a', '/abab', '/b', '/c/a/b/d'],
                          filter_children_in_paths(paths))
