from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.trash.tests import duplicate_with_dexterity
from ftw.trash.tests import FunctionalTestCase
from ftw.trash.trasher import Trasher
import transaction


@duplicate_with_dexterity
class TestTraversing(FunctionalTestCase):

    @browsing
    def test_browsing_trashed_content_raises_404(self, browser):
        self.grant('Contributor')

        parent = create(Builder('folder'))
        folder = create(Builder('folder').within(parent))
        subfolder = create(Builder('folder').within(folder))

        browser.login()
        # the user can access all content, since none is trashed
        browser.open(parent)
        browser.open(folder)
        browser.open(subfolder)

        # when we trash "folder", the parent is still accessible, but not the trashed content
        Trasher(folder).trash()
        transaction.commit()

        browser.open(parent)

        with browser.expect_http_error(404):
            browser.open(folder)

        with browser.expect_http_error(404):
            browser.open(subfolder)

    @browsing
    def test_allow_Manager_to_browse_trashed_content_with_status_message(self, browser):
        self.grant('Manager')

        folder = create(Builder('folder').titled(u'Fancy Folder'))
        browser.login()
        browser.open(folder)

        Trasher(folder).trash()
        transaction.commit()
        browser.open(folder)

        statusmessages.assert_message('The content "Fancy Folder" is trashed.')
