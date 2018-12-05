# -*- coding: utf-8 -*-

from imio.restapi.services import add

from plone.restapi.deserializer import json_body

from urban.restapi.exceptions import UndefinedPortalType

from Products.urban.utils import getLicenceFolder

import json


class AddLicencePost(add.FolderPost):

    portal_type = ''  # to override in subclasses

    def reply(self):
        data = json_body(self.request)
        data = self.set_portal_type(data)
        data = self.set_creation_place(data)
        self.request.set('BODY', json.dumps(data))
        result = super(AddLicencePost, self).reply()
        return result

    def set_portal_type(self, data):
        """ """
        if self.portal_type:
            data['@type'] = self.portal_type
        return data

    def set_creation_place(self, data):
        """ """
        portal_type = data.get('@type', None)
        if not portal_type:
            raise UndefinedPortalType
        licence_folder = getLicenceFolder(portal_type)
        self.context = licence_folder
        return data

    def set_default_foldermanager(self):
        """ """
