# -*- coding: utf-8 -*-

from urban.restapi.services.content.licence import base

import json

from urban.restapi.services.content.utils import set_rubrics


class AddLicencePost(base.AddLicencePost):

    def reply(self):
        data = json_body(self.request)
        for licence in data['__children__']:
            new_data = set_rubrics(licence)
            self.request.set('BODY', json.dumps(new_data))
            result = super(AddLicencePost, self).reply()
        return result
