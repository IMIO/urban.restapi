# -*- coding: utf-8 -*-

from urban.restapi.services.content.licence import environment_base


class AddEnvClassThreePost(environment_base.AddLicencePost):

    portal_type = 'EnvClassThree'

    def reply(self):
        result = super(AddEnvClassThreePost, self).reply()
        return result
