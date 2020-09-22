# -*- coding: utf-8 -*-

from imio.restapi.services import add
from plone import api

from plone.restapi.deserializer import json_body
from plone.restapi.services.content import get


import json

from Products.urban.interfaces import IGenericLicence
from urban.restapi.services.content.utils import set_creation_place, set_default_foldermanager


class AddLicencePost(add.FolderPost):

    portal_type = ''  # to override in subclasses

    def reply(self):
        licence = json_body(self.request)
        licence = set_creation_place(self, licence)
        licence = set_default_foldermanager(self, licence)
        self.request.set('BODY', json.dumps(licence))
        result = super(AddLicencePost, self).reply()
        return result


class LicenceStatus(get.ContentGet):

    portal_type = ''

    def reply(self):
        reference = self.request.ref
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(object_provides='Products.urban.interfaces.IEnvClassThree')
        results = []
        for brain in brains:
            if brain.getObject().getReference() == reference:
                results.append(brain.getObject())
        if len(results) == 1:
            workflow_tool = api.portal.get_tool('portal_workflow')
            workflow_state = workflow_tool.getStatusOf('urban_licence_workflow', results[0])
            response = {'review_state': workflow_state['review_state'],
                        'date': str(workflow_state['time'].Date())}
            return response
        else:
            return {'error': 'too many or no result(s)'}
