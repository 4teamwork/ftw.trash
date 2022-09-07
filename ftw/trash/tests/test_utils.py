import unittest
from ftw.trash.testing import FTW_TRASH_FUNCTIONAL_TESTING


from ftw.trash.utils import filter_children_in_paths, is_trash_profile_installed

class TestUtilsWhenInstalled(unittest.TestCase):
    layer = FTW_TRASH_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]

    def test_is_trash_profile_installed(self):
        self.assertTrue(is_trash_profile_installed())


class TestFilterChildrenInPaths(unittest.TestCase):
    def test(self):
        paths = ["/a/b/c/d", "/a", "/b", "/a/b/c/d/e/f", "/c/a/b/d", "/abab"]
        self.assertEquals(
            ["/a", "/abab", "/b", "/c/a/b/d"], filter_children_in_paths(paths)
        )
