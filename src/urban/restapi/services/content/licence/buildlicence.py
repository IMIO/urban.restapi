# -*- coding: utf-8 -*-

from urban.restapi.services.content.licence import base


class AddBuildLicencePost(base.AddLicencePost):

    portal_type = 'BuildLicence'

    def reply(self):
        result = super(AddBuildLicencePost, self).reply()
        return result
