# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import (
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
    applyProfile,
)
from plone.testing import z2

import ftw.upgrade
import ftw.trash


class FtwTrashLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=ftw.upgrade)
        self.loadZCML(package=ftw.trash)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "ftw.trash:default")


SITE_OWNER_NAME = "admin"
SITE_OWNER_PASSWORD = "admin"

FTW_TRASH_FIXTURE = FtwTrashLayer()


FTW_TRASH_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_TRASH_FIXTURE,),
    name="FtwTrashLayer:IntegrationTesting",
)


FTW_TRASH_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_TRASH_FIXTURE,),
    name="FtwTrashLayer:FunctionalTesting",
)


FTW_TRASH_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        FTW_TRASH_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="FtwTrashLayer:AcceptanceTesting",
)
