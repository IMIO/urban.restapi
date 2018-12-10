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
        data = self.set_location_uids(data)
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

    def set_location_uids(self, data):
        """ """
        catalog = api.portal.get_tool("uid_catalog")
        results = catalog.searchResults(**{'portal_type': 'Street'})
        if 'workLocations' in data and data['workLocations']:
            for idx, work_location in enumerate(data['workLocations']):
                if not('street' in work_location) and 'street_ins' in work_location:
                    for result in results:
                        if data['workLocations'][idx]['street_ins'] == result.getObject().getStreetCode():
                            data['workLocations'][idx]['street'] = result.getObject().UID()
                            break

        if 'businessOldLocation' in data and data['businessOldLocation']:
            for idx, business_old_location in enumerate(data['businessOldLocation']):
                if not ('street' in business_old_location) and 'street_ins' in business_old_location:
                    for result in results:
                        if data['businessOldLocation'][idx]['street_ins'] == result.getObject().getStreetCode():
                            data['businessOldLocation'][idx]['street'] = result.getObject().UID()
                            break
        return data
