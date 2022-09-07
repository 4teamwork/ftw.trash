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

        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        
        parent = api.content.create(
            container=self.portal,
            type="Folder",
            id="parent",
            title="Parent",
        )
        folder = api.content.create(
            container=parent, 
            type="Folder", 
            id="foo", 
            title="Foo"
        )
        subfolder = api.content.create(
            container=parent, 
            type="Folder", 
            id="bar", 
            title="Bar"
        )

        self.browser.open(self.portal_url + "/parent")
        self.browser.open(self.portal_url + "/folder")
        self.browser.open(self.portal_url + "/subfolder")

        Trasher(folder).trash()
        transaction.commit()

        with self.browser.expect_http_error(404):
            self.browser.open(self.portal_url + "/folder")

        with self.browser.expect_http_error(404):
            self.browser.open(self.portal_url + "/subfolder")

    def test_allow_Manager_to_browse_trashed_content_with_status_message(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="parent",
            title="Fancy Folder",
        )

        self.browser.open(self.portal_url + "/folder")

        Trasher(folder).trash()
        transaction.commit()
        self.browser.open(self.portal_url + "/folder")
        assert('The content "Fancy Folder" is trashed.' in self.browser.content)
    
