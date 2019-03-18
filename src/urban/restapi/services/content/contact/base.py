# -*- coding: utf-8 -*-

from imio.restapi.services import add
from plone.restapi.deserializer import json_body

import json


class AddContactPost(add.FolderPost):

    portal_type = ''  # to override in subclasses

    def reply(self):
        contacts = json_body(self.request)
        for contact in contacts["__elements__"]:
            contact = self.set_portal_type(contact)
            self.request.set('BODY', json.dumps(contact))
            result = super(AddContactPost, self).reply()
        return result

    def set_portal_type(self, data):
        """ """
        if self.portal_type:
            data['@type'] = self.portal_type
        return data
