# -*- coding: utf-8 -*-

from imio.restapi.services import add
from plone.restapi.deserializer import json_body

import json


class AddElementPost(add.FolderPost):

    portal_type = ''  # to override in subclasses

    def reply(self):
        elements = json_body(self.request)
        for element in elements["__elements__"]:
            element = self.set_portal_type(element)
            self.request.set('BODY', json.dumps(element))
            result = super(AddElementPost, self).reply()
        return result

    def set_portal_type(self, data):
        """ """
        if self.portal_type:
            data['@type'] = self.portal_type
        return data
