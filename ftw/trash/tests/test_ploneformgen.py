from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import IS_PLONE_5
from ftw.testing.mailing import Mailing
from ftw.trash.interfaces import ITrashed
from ftw.trash.tests import FunctionalTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


class TestPloneFormGen(FunctionalTestCase):
    def setUp(self):
        super(TestPloneFormGen, self).setUp()
        self.grant('Manager')

        # Set Missing Property, so mailing wont fail
        if IS_PLONE_5:
            from Products.CMFPlone.interfaces import IMailSchema
            registry = getUtility(IRegistry)
            mail_settings = registry.forInterface(IMailSchema, prefix='plone')
            mail_settings.email_from_address = 'foo@bar.ch'
        else:
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

    @browsing
    def test_ploneformgen_field_not_required(self, browser):
        form_folder = create(Builder('FormFolder'))
        form_folder.manage_delObjects(['replyto'])
        transaction.commit()

        browser.login().visit(form_folder)
        browser.find_form_by_field('Subject').fill({
            'Subject': 'Foo',
             'Comments': 'Bar'
        }).submit()

        self.assertNotIn('This field is required.', browser.css('.fieldErrorBox').text)

    @browsing
    def test_ploneformgen_adapters_dont_run(self, browser):
        Mailing(self.layer['portal']).set_up()

        form_folder = create(Builder('FormFolder'))
        form_folder.manage_delObjects(['mailer'])
        transaction.commit()

        browser.login().visit(form_folder)
        browser.find_form_by_field('Subject').fill({
            'Your E-Mail Address': 'foo@bar.ch',
            'Subject': 'Foo',
            'Comments': 'Bar'
        }).submit()

        self.assertFalse(Mailing(self.portal).has_messages())
