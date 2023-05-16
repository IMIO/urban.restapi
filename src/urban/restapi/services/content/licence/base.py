# -*- coding: utf-8 -*-

from imio.restapi.services import add

from plone import api

from plone.restapi.deserializer import json_body

from urban.restapi.exceptions import UndefinedPortalType, DefaultFolderManagerNotFoundError
from urban.restapi.services.content.utils import get_config_object

from Products.urban.utils import getLicenceFolder

import json


class AddLicencePost(add.FolderPost):

    portal_type = ''  # to override in subclasses

    def reply(self):
        elements = json_body(self.request)
        result_list = []
        for element in elements["__elements__"]:
            licence = self.initialize_description_field(element)
            licence = self.set_portal_type(licence)
            licence = self.set_creation_place(licence)
            licence = self.set_default_foldermanager(licence)
            licence = self.set_location_uids(licence)
            licence = self.set_events(licence)
            licence = self.set_contacts(licence)
            self.request.set('BODY', json.dumps(licence))
            result_list.append(super(AddLicencePost, self).reply())
        return result_list

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
                else:
                    zipcode = data['workLocations'][idx]['zipcode'] if 'zipcode' in data['workLocations'][idx] else ""
                    localite = data['workLocations'][idx]['localite'] if 'localite' in data['workLocations'][idx] else ""
                    data['description']['data'] += ("<p>Situation : %s %s %s %s</p>" %
                                                    (
                                                        data['workLocations'][idx]['number'],
                                                        data['workLocations'][idx]['street'],
                                                        zipcode,
                                                        localite
                                                    ))

        if 'businessOldLocation' in data and data['businessOldLocation']:
            for idx, business_old_location in enumerate(data['businessOldLocation']):
                if not ('street' in business_old_location) and 'street_ins' in business_old_location:
                    for result in results:
                        if data['businessOldLocation'][idx]['street_ins'] == result.getObject().getStreetCode():
                            data['businessOldLocation'][idx]['street'] = result.getObject().UID()
                            break
                else:
                    zipcode = data['businessOldLocation'][idx]['zipcode'] \
                        if 'zipcode' in data['businessOldLocation'][idx] else ""
                    localite = data['businessOldLocation'][idx]['localite'] \
                        if 'localite' in data['businessOldLocation'][idx] else ""
                    data['description']['data'] += ("<p>Ancienne adresse de l'exploitation : %s %s %s %s</p>" %
                                                    (
                                                        data['businessOldLocation'][idx]['number'],
                                                        data['businessOldLocation'][idx]['street'],
                                                        zipcode,
                                                        localite
                                                    ))
        return data

    def set_events(self, data):
        """ """
        if '__children__' in data:
            for idx, child in enumerate(data['__children__']):
                if child['@type'] == 'UrbanEvent':
                    if child['event_id'] and 'urbaneventtypes' not in child:
                        data['__children__'][idx]['urbaneventtypes'] = "{0}/portal_urban/{1}/urbaneventtypes/{2}".format(
                            api.portal.getSite().absolute_url(),
                            self.portal_type.lower(),
                            child['event_id']
                    )
        return data

    def set_contacts(self, data):
        """ """
        catalog = api.portal.get_tool('portal_catalog')

        if 'architects' in data and data['architects']:
            architects_args = []
            for idx, architect in enumerate(data['architects']):
                if not ('architect_id' in architect):
                    fullname = "{0} {1}".format(architect['name1'], architect['name2'])
                    if fullname:
                        architects = catalog(portal_type='Architect', Title=fullname)
                        if len(architects) == 1:
                            architects_args.append(architects[0].getObject().absolute_url())
                        else:
                            data['description']['data'] += (u"<p>Architecte : %s %s %s %s %s</p>" % (
                                                                architect.get('name1', ""),
                                                                architect.get('name2', ""),
                                                                architect.get('street', ""),
                                                                architect.get('zipcode', ""),
                                                                architect.get('city', "")
                                                            ))
                    else:
                        print("Empty architect ?")
                else:
                    architects_args.append(architect['architect_id'])

            if architects_args:
                data['architects'] = architects_args

        if 'geometricians' in data and data['geometricians']:
            geometricians_args = []
            for idx, geometrician in enumerate(data['geometricians']):
                if not ('geometrician_id' in geometrician):
                    fullname = "{0} {1}".format(geometrician['name1'], geometrician['name2'])
                    if fullname:
                        geometricians = catalog(portal_type='Geometrician', Title=fullname)
                        if len(geometricians) == 1:
                            geometricians_args.append(geometricians[0].getObject().absolute_url())
                        else:
                            data['description']['data'] += (u"<p>Géomètre : %s %s %s %s %s</p>" %
                                                            (
                                                                geometrician.get('name1', ""),
                                                                geometrician.get('name2', ""),
                                                                geometrician.get('street', ""),
                                                                geometrician.get('zipcode', ""),
                                                                geometrician.get('city', "")
                                                            ))
                    else:
                        print("Empty geometrician ?")
                else:
                    geometricians_args.append(geometrician['geometrician_id'])

            if geometricians_args:
                data['geometricians'] = geometricians_args

        if 'notaries' in data and data['notaries']:
            notaries_args = []
            for idx, notary in enumerate(data['notaries']):
                if not ('notary_id' in notary):
                    fullname = "{0} {1}".format(notary['name1'], notary['name2'])
                    if fullname:
                        notaries = catalog(portal_type='Notary', Title=fullname)
                        if len(notaries) == 1:
                            notaries_args.append(notaries[0].getObject().absolute_url())
                        else:
                            data['description']['data'] += (u"<p>Notaire : %s %s %s %s %s</p>" %
                                                            (
                                                                notary.get('name1', ""),
                                                                notary.get('name2', ""),
                                                                notary.get('street', ""),
                                                                notary.get('zipcode', ""),
                                                                notary.get('city', "")
                                                            ))
                    else:
                        print("Empty notary ?")
                else:
                    notaries_args.append(notary['notary_id'])

            if notaries_args:
                data['notaries'] = notaries_args

        return data

    @staticmethod
    def initialize_description_field(data):
        if 'description' not in data:
            data['description'] = {}
        if 'data' not in data['description']:
            data['description']['data'] = ""
        if 'content-type' not in data['description']:
            data['description']['content-type'] = "text/html"

        return data


class AddLicenceChildPost(add.FolderPost):
    def prepare_data(self, data):
        data = super(AddLicenceChildPost, self).prepare_data(data)

        if u"urbaneventtypes" in data:
            try:
                config = get_config_object(
                    "{0}/eventconfigs/{1}".format(
                        self.context.portal_type.lower(), data["urbaneventtypes"]
                    )
                )
                data["urbaneventtypes"] = config.UID()
            except KeyError:
                return data

        return data
