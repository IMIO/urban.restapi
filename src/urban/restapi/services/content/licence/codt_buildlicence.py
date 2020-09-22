# -*- coding: utf-8 -*-

from urban.restapi.services.content.licence import base


class AddCodtBuildLicencePost(base.AddLicencePost):

    portal_type = 'CODT_BuildLicence'

    def reply(self):
        result = super(AddCodtBuildLicencePost, self).reply()
        return result
