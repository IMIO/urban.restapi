# -*- coding: utf-8 -*-

from imio.restapi.services import add

from plone.restapi.deserializer import json_body


import json

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

    @staticmethod
    def initialize_description_field(data):
        if 'description' not in data:
            data['description'] = {}
        if 'data' not in data['description']:
            data['description']['data'] = ""
        if 'content-type' not in data['description']:
            data['description']['content-type'] = "text/html"

        return data
