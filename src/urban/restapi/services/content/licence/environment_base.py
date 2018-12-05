# -*- coding: utf-8 -*-

from plone import api
from plone.restapi.deserializer import json_body
from urban.restapi.exceptions import EnvironmentRubricNotFound
from urban.restapi.services.content.licence import base

import json


class AddLicencePost(base.AddLicencePost):

    def reply(self):
        data = json_body(self.request)
        new_data = self.set_rubrics(data)
        self.request.set('BODY', json.dumps(new_data))
        result = super(AddLicencePost, self).reply()
        return result

    def set_rubrics(self, data):
        """ """
        rubrics_args = data.get(u'rubrics', '')
        data[u'rubrics'] = []

        if rubrics_args:
            catalog = api.portal.get_tool('portal_catalog')
            rubric_uids = []
            for rubric in rubrics_args:
                rubric_brains = catalog(id=rubric)
                if len(rubric_brains) != 1:
                    raise EnvironmentRubricNotFound(rubric)
                rubric_uids.append(rubric_brains[0].UID)
            data[u'rubrics'] = rubric_uids
        return data
