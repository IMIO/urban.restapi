# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from urban.restapi.testing import URBAN_RESTAPI_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that urban.restapi is properly installed."""

    layer = URBAN_RESTAPI_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if urban.restapi is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'urban.restapi'))

    def test_browserlayer(self):
        """Test that IUrbanRestapiLayer is registered."""
        from urban.restapi.interfaces import (
            IUrbanRestapiLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IUrbanRestapiLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = URBAN_RESTAPI_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['urban.restapi'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if urban.restapi is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'urban.restapi'))

    def test_browserlayer_removed(self):
        """Test that IUrbanRestapiLayer is removed."""
        from urban.restapi.interfaces import \
            IUrbanRestapiLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IUrbanRestapiLayer,
            utils.registered_layers())
