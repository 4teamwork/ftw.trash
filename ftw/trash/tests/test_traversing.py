from ftw.trash.testing import FTW_TRASH_FUNCTIONAL_TESTING
from ftw.trash.trasher import Trasher

from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID, setRoles
from plone.testing.zope import Browser

import transaction
import unittest


class TestTraversing(unittest.TestCase):
    layer = FTW_TRASH_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()

        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization",
            "Basic {username}:{password}".format(
                username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD
            ),
        )

    def test_browsing_trashed_content_raises_404(self):
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
        top = api.content.create(
            container=self.portal,
            type="Folder",
            id="top",
            title="Top Folder",
        )

        api.content.create(container=top, type="Folder", id="foo", title="Foo")
        api.content.create(container=top, type="Folder", id="bar", title="Bar")
        transaction.commit()

        self.browser.open(self.portal_url + "/top")
        self.browser.open(self.portal_url + "/top/foo")
        self.browser.open(self.portal_url + "/top/bar")

        Trasher(top).trash()
        transaction.commit()

        self.browser.handleErrors = True

        self.browser.open(self.portal_url + "/top/foo")
        assert 'The content "Foo" is trashed.' in self.browser.contents

        self.browser.open(self.portal_url + "/top/bar")
        assert 'The content "Bar" is trashed.' in self.browser.contents

    def test_allow_Manager_to_browse_trashed_content_with_status_message(self):
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])

        top = api.content.create(
            container=self.portal,
            type="Folder",
            id="top",
            title="Fancy Folder",
        )
        transaction.commit()
        self.browser.open(self.portal_url + "/top")

        Trasher(top).trash()
        transaction.commit()
        self.browser.open(self.portal_url + "/top")

        assert 'The content "Fancy Folder" is trashed.' in self.browser.contents