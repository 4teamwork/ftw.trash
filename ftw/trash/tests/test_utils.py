from ftw.trash.testing import TRASH_NOT_INSTALLED_FUNCTIONAL
from ftw.trash.tests import FunctionalTestCase
from ftw.trash.utils import is_trash_profile_installed


class TestUtilsWhenInstalled(FunctionalTestCase):

    def test_is_trash_profile_installed(self):
        self.assertTrue(is_trash_profile_installed())


class TestUtilsWhenNotInstalled(FunctionalTestCase):
    layer = TRASH_NOT_INSTALLED_FUNCTIONAL

    def test_is_trash_profile_installed(self):
        self.assertFalse(is_trash_profile_installed())
