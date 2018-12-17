from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testing import IS_PLONE_5
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig


class TrashLayer(PloneSandboxLayer):
    defaultBases = (COMPONENT_REGISTRY_ISOLATION, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '  <include package="ftw.trash.tests" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.trash')
        z2.installProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.trash:default')
        applyProfile(portal, 'ftw.trash.tests:dxtests')
        applyProfile(portal, 'Products.PloneFormGen:default')

        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')


TRASH_FIXTURE = TrashLayer()
TRASH_FUNCTIONAL = FunctionalTesting(
    bases=(TRASH_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.trash:functional")


class TrashNotInstalledLayer(PloneSandboxLayer):
    """In the this layer, the ftw.trash package's ZCML is loaded but the Generic Setup
    profile is not installed.
    Loading of the ZCML is important as it would also happen in the production and it will
    apply patches, but the patches should only change behavior when also the Generic Setup
    profile is installed.
    """
    defaultBases = (COMPONENT_REGISTRY_ISOLATION, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '  <include package="ftw.trash.tests" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.trash')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.trash.tests:dxtests')
        applyProfile(portal, 'collective.deletepermission:default')

        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')


TRASH_NOT_INSTALLED_FUNCTIONAL = FunctionalTesting(
    bases=(TrashNotInstalledLayer(),
           set_builder_session_factory(functional_session_factory)),
    name="ftw.trash:not-installed:functional")
