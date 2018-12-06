# -*- coding: utf-8 -*-

from imio.restapi.services import add

from plone import api

from plone.restapi.deserializer import json_body

from urban.restapi.exceptions import UndefinedPortalType, DefaultFolderManagerNotFoundError

from Products.urban.utils import getLicenceFolder

import json


class AddLicencePost(add.FolderPost):

    portal_type = ''  # to override in subclasses

    def reply(self):
        data = json_body(self.request)
        data = self.set_portal_type(data)
        data = self.set_creation_place(data)
        data = self.set_default_foldermanager(data)
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

    def set_default_foldermanager(self, data):
        """ """
        if not ('foldermanagers' in data and data['foldermanagers']):
            portal_urban = api.portal.get_tool('portal_urban')
            for licence_config in portal_urban.objectValues('LicenceConfig'):
                if licence_config.id == data.get('@type').lower():
                    default_foldermanagers_uids = [foldermanager.UID()
                                                   for foldermanager in licence_config.getDefault_foldermanager()]
                    data['foldermanagers'] = default_foldermanagers_uids

            if not data['foldermanagers']:
                raise DefaultFolderManagerNotFoundError(["No default foldermanager for this licence type"])
        return data
