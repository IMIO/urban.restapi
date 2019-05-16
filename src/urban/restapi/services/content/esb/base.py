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
