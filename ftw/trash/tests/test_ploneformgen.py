from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.trash.interfaces import ITrashed
from ftw.trash.tests import FunctionalTestCase
import transaction


class TestPloneFormGen(FunctionalTestCase):
    def setUp(self):
        super(TestPloneFormGen, self).setUp()
        self.grant('Manager')

        # Set Missing Property, so mailing wont fail
        self.portal._updateProperty('email_from_address', 'foo@bar.ch')

    @browsing
    def test_ploneformgen_removes_trashed_fields(self, browser):
        form_folder = create(Builder('FormFolder'))

        reply_to = form_folder.get('replyto')
        self.assertIn(reply_to, form_folder._getFieldObjects())

        browser.login().visit(form_folder)
        self.assertTrue(browser.find('Your E-Mail Address'))

        form_folder.manage_delObjects([reply_to.id])
        transaction.commit()

        self.assertTrue(ITrashed.providedBy(reply_to))
        self.assertNotIn(reply_to, form_folder._getFieldObjects())

        browser.reload()
        self.assertFalse(browser.find('Your E-Mail Address'))
