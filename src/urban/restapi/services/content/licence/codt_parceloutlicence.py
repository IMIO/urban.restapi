# -*- coding: utf-8 -*-

from urban.restapi.services.content.licence import base


class AddCodtParcelOutLicencePost(base.AddLicencePost):

    portal_type = 'CODT_ParcelOutLicence'

    def reply(self):
        result = super(AddCodtParcelOutLicencePost, self).reply()
        return result
