from ftw.trash.testing import FTW_TRASH_FUNCTIONAL_TESTING
from ftw.trash.trasher import Trasher
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID, setRoles
from plone.testing.zope import Browser
import transaction
import unittest


class TestZMI(unittest.TestCase):
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

    def test_delete_from_ZMI_does_actually_delete_content(self):
        self.browser.open(self.portal_url + "/++add++Folder")
        self.browser.getControl(name="form.widgets.IDublinCore.title").value = "Foo"
        self.browser.getControl("Save").click()
        self.assertTrue("<h1>Foo</h1>" in self.browser.contents)

        self.browser.open(self.portal_url + "/foo/++add++Folder")
        self.browser.getControl(name="form.widgets.IDublinCore.title").value = "Bar"
        self.browser.getControl("Save").click()
        self.assertTrue("<h1>Bar</h1>" in self.browser.contents)

        self.browser.open(f"{self.portal_url}/foo/manage_main")
        self.assertEquals(["bar"], self.browser.getControl(name="ids:list").options)
        self.browser.getControl(name="ids:list").getControl("bar").selected = True
        self.browser.getControl(name="manage_delObjects:method").click()
        self.assertIn("There are currently no items in", self.browser.contents)

    def test_manager_can_delete_trashed_content(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="foo",
            title="Foo",
        )
        api.content.create(
            container=folder,
            type="Folder",
            id="normal",
            title="Normal",
        )
        trashed = api.content.create(
            container=folder,
            type="Folder",
            id="trashed",
            title="Trashed Folder",
        )

        Trasher(trashed).trash()
        self.assertEqual(["normal", "trashed"], folder.objectIds())
        transaction.commit()

        self.browser.open(f"{self.portal_url}/foo/manage_main")
        self.assertEquals(
            ["normal", "trashed"], self.browser.getControl(name="ids:list").options
        )

        self.browser.getControl(name="ids:list").getControl("trashed").selected = True
        self.browser.getControl(name="manage_delObjects:method").click()
        self.assertEquals(["normal"], self.browser.getControl(name="ids:list").options)
