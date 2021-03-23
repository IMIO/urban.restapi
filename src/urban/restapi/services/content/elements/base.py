# -*- coding: utf-8 -*-

import json

from Products.CMFPlone.utils import normalizeString
from imio.restapi.services import add
from plone import api
from plone.api.exc import InvalidParameterError
from plone.restapi.deserializer import json_body
from urban.restapi.exceptions import UndefinedPortalType, DefaultFolderManagerNotFoundError, EnvironmentRubricNotFound
from urban.restapi.services.content.utils import quote_parenthesis
from Products.urban.utils import getLicenceFolder


class AddElementPost(add.FolderPost):

    portal_type = ''  # to override in subclasses

    def reply(self):
        elements = json_body(self.request)
        for element in elements["__elements__"]:
            element = self.set_portal_type(element)
            licence = self.initialize_description_field(element)
            licence = self.set_creation_place(licence)
            licence = self.set_default_foldermanager(licence)
            licence = self.set_location_uids(licence)
            licence = self.set_events(licence)
            licence = self.set_rubrics(licence)
            licence = self.set_contacts(licence)
            self.request.set('BODY', json.dumps(licence))
            result = super(AddElementPost, self).reply()
            # post-treatment
            self.set_status(licence, result)
            self.set_location_number_format(licence, result)
        return result

    def set_portal_type(self, data):
        """ """
        if self.portal_type:
            data['@type'] = self.portal_type
        else:
            data['@type'] = data['portalType']
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
                if data['workLocations'][idx]['number']:
                    data['workLocations'][idx]['number'] = str(data['workLocations'][idx]['number'])
                if 'bestaddress_key' in work_location and work_location['bestaddress_key']:
                    for result in results:
                        if int(data['workLocations'][idx]['bestaddress_key']) == result.getObject().getBestAddressKey():
                            data['workLocations'][idx]['street'] = str(result.getObject().UID())

                            break
                else:
                    zipcode = data['workLocations'][idx]['zipcode'] if 'zipcode' in data['workLocations'][idx] else ""
                    localite = data['workLocations'][idx]['locality'] if 'locality' in data['workLocations'][idx] else ""
                    data['description']['data'] += ("<p>Situation : %s %s %s %s</p>" %
                                                    (
                                                        data['workLocations'][idx]['number'],
                                                        data['workLocations'][idx]['street'],
                                                        zipcode,
                                                        localite
                                                    ))

        if 'businessOldLocation' in data and data['businessOldLocation']:
            for idx, business_old_location in enumerate(data['businessOldLocation']):
                if 'bestaddress_key' in business_old_location and business_old_location['bestaddress_key']:
                    for result in results:
                        if int(data['business_old_location'][idx]['bestaddress_key']) == result.getObject().getBestAddressKey():
                            data['businessOldLocation'][idx]['street'] = result.getObject().UID()
                            break
                else:
                    zipcode = data['businessOldLocation'][idx]['zipcode'] \
                        if 'zipcode' in data['businessOldLocation'][idx] else ""
                    localite = data['businessOldLocation'][idx]['locality'] \
                        if 'locality' in data['businessOldLocation'][idx] else ""
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
                            data['@type'].lower(),
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
                    fullname = u"{0} {1}".format(architect['name1'], architect['name2'])
                    if fullname:
                        architects = catalog(portal_type='Architect', Title=quote_parenthesis(fullname).replace("-", " "))
                        if len(architects) == 1:
                            architects_args.append(architects[0].getObject().absolute_url())
                        elif len(architects) == 0 and architect['force_create'] == 'True':
                            container = api.content.get(path='/urban/architects')
                            normalized_id = normalizeString(u"{}_{}".format(architect.get('name1', ""), architect.get('name2', "")))
                            object_id = container.invokeFactory('Architect',
                                                                id= normalized_id,
                                                                name1=architect.get('name1', ""),
                                                                name2=architect.get('name2', ""),
                                                                phone=architect.get('phone', ""),
                                                                gsm=architect.get('gsm', ""),
                                                                email=architect.get('email', ""),
                                                                personTitle=architect.get('personTitle', ""),
                                                                street=architect.get('street', ""),
                                                                zipcode=str(architect.get('zipcode', "")),
                                                                city=architect.get('city', ""))
                            architects = catalog(portal_type='Architect', id=object_id)
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

            data['architects'] = architects_args

        if 'geometricians' in data and data['geometricians']:
            geometricians_args = []
            for idx, geometrician in enumerate(data['geometricians']):
                if not ('geometrician_id' in geometrician):
                    fullname = u"{0} {1}".format(geometrician['name1'], geometrician['name2'])
                    if fullname:
                        geometricians = catalog(portal_type='Geometrician', Title=quote_parenthesis(fullname))
                        if len(geometricians) == 1:
                            geometricians_args.append(geometricians[0].getObject().absolute_url())
                        elif len(geometricians) == 0 and geometrician['force_create'] == 'True':
                            container = api.content.get(path='/urban/geometricians')
                            normalized_id = normalizeString(u"{}_{}".format(geometrician.get('name1', ""), geometrician.get('name2', "")))
                            object_id = container.invokeFactory('Geometrician',
                                                                id= normalized_id,
                                                                name1=geometrician.get('name1', ""),
                                                                name2=geometrician.get('name2', ""),
                                                                phone=geometrician.get('phone', ""),
                                                                gsm=geometrician.get('gsm', ""),
                                                                email=geometrician.get('email', ""),
                                                                personTitle=geometrician.get('personTitle', ""),
                                                                street=geometrician.get('street', ""),
                                                                zipcode=str(geometrician.get('zipcode', "")),
                                                                city=geometrician.get('city', ""))
                            geometricians = catalog(portal_type='Geometrician', id=object_id)
                            geometricians_args.append(geometricians[0].getObject().absolute_url())
                        elif len(geometricians) > 1 and geometrician['force_create'] == 'True':
                            fullname_default = u"Géomètre par défaut"
                            geometricians = catalog(portal_type='Geometrician', Title=fullname_default)
                            if len(geometricians) == 1:
                                geometricians_args.append(geometricians[0].getObject().absolute_url())
                                data['description']['data'] += (u"<p>Trop de résultats pour le géomètre %s, un géomètre par défaut a été lié</p>" %
                                                                (
                                                                    fullname
                                                                ))
                            else:
                                print("Pas de géomètre défini par défaut : {}".format(fullname_default))
                        else:
                            data['description']['data'] += (u"<p>Géomètre : %s %s %s %s %s</p>" %
                                                            (
                                                                geometrician.get('name1', ""),
                                                                geometrician.get('name2', ""),
                                                                geometrician.get('street', ""),
                                                                str(geometrician.get('zipcode', "")),
                                                                geometrician.get('city', "")
                                                            ))
                    else:
                        print("Empty geometrician ?")

                else:
                    geometricians_args.append(geometrician['geometrician_id'])

            data['geometricians'] = geometricians_args

        if 'notaries' in data and data['notaries']:
            notaries_args = []
            for idx, notary in enumerate(data['notaries']):
                if not ('notary_id' in notary):
                    fullname = u"{0} {1}".format(notary['name1'], notary['name2'])
                    if fullname:
                        notaries = catalog(portal_type='Notary', Title=quote_parenthesis(fullname).replace("-", " "))
                        if len(notaries) == 1:
                            notaries_args.append(notaries[0].getObject().absolute_url())
                        elif len(notaries) == 0 and notary['force_create'] == 'True':
                            container = api.content.get(path='/urban/notaries')
                            normalized_id = normalizeString(u"{}_{}".format(notary.get('name1', ""), notary.get('name2', "")))
                            object_id = container.invokeFactory('Notary',
                                                                id= normalized_id,
                                                                name1=notary.get('name1', ""),
                                                                name2=notary.get('name2', ""),
                                                                phone=notary.get('phone', ""),
                                                                gsm=notary.get('gsm', ""),
                                                                email=notary.get('email', ""),
                                                                personTitle=notary.get('personTitle', ""),
                                                                street=notary.get('street', ""),
                                                                zipcode=str(notary.get('zipcode', "")),
                                                                city=notary.get('city', ""))
                            notaries = catalog(portal_type='Notary', id=object_id)
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

            data['notaryContact'] = notaries_args

        return data

    def set_status(self, licence, result):
        if 'wf_state' in licence and licence['wf_state']:
            site = api.portal.getSite()
            licence_object = site.reference_catalog.lookupObject(result['UID'])
            try:
                api.content.transition(licence_object, licence['wf_state'])
            except InvalidParameterError:
                print("***no valid state***")

        if 'wf_transition' in licence and licence['wf_transition']:
            site = api.portal.getSite()
            licence_object = site.reference_catalog.lookupObject(result['UID'])
            try:
                api.content.transition(obj=licence_object, to_state=licence['wf_transition'])
            except InvalidParameterError:
                print("***no valid transition***")
                # api.content.transition(licence_object, 'nonapplicable')
        return licence

    def set_location_number_format(self, licence, result):
        if 'workLocations' in licence and licence['workLocations']:
            site = api.portal.getSite()
            licence_object = site.reference_catalog.lookupObject(result['UID'])
            wl = licence_object.getWorkLocations()
            wll = list(wl)
            new_wll = []
            for wl in wll:
                if wl['number'] and isinstance(wl['number'], unicode):
                    wl['number'] = wl['number'].encode("utf-8")
                new_wll.append(wl)
            licence_object.setWorkLocations(tuple(new_wll))

    def set_rubrics(self, data):
        """ """
        rubrics_args = data.get(u'rubrics', '')
        data[u'rubrics'] = []

        if rubrics_args:
            catalog = api.portal.get_tool('portal_catalog')
            rubric_uids = []
            for rubric in rubrics_args:
                rubric_brains = catalog(id=rubric, portal_type='EnvironmentRubricTerm')
                if len(rubric_brains) != 1:
                    print(u"***Environment Rubric Not Found or too many results: {} ***".format(rubric.encode("ascii", "ignore")))
                else:
                    rubric_uids.append(rubric_brains[0].UID)
            data[u'rubrics'] = rubric_uids
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
