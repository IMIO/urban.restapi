# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.restapi.testing import PLONE_RESTAPI_AT_FUNCTIONAL_TESTING
from plone.testing import z2

import urban.restapi


class UrbanRestapiLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        self.loadZCML(package=urban.restapi)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'urban.restapi:default')


URBAN_RESTAPI_FIXTURE = UrbanRestapiLayer()


URBAN_RESTAPI_INTEGRATION_TESTING = IntegrationTesting(
    bases=(URBAN_RESTAPI_FIXTURE,),
    name='UrbanRestapiLayer:IntegrationTesting',
)


URBAN_RESTAPI_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(URBAN_RESTAPI_FIXTURE, PLONE_RESTAPI_AT_FUNCTIONAL_TESTING),
    name='UrbanRestapiLayer:FunctionalTesting',
)


URBAN_RESTAPI_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        URBAN_RESTAPI_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='UrbanRestapiLayer:AcceptanceTesting',
)
