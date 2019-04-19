# -*- coding: utf-8 -*-

from plone.restapi.deserializer import json_body
from urban.restapi.services.content.licence import environment_base

import json


class AddEnvClassThreePost(environment_base.AddLicencePost):

    portal_type = 'EnvClassThree'

    def reply(self):
        result = super(AddEnvClassThreePost, self).reply()
        return result
