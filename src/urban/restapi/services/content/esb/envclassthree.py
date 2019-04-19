# -*- coding: utf-8 -*-

import base64
import json

from plone.restapi.deserializer import json_body
from urban.restapi.services.content.esb import base
from urban.restapi.services.content.utils import set_rubrics, set_location


class AddEsbEnvClassThreePost(base.AddLicencePost):

    portal_type = 'EnvClassThree'

    def reply(self):
        body = json_body(self.request)
        archive_title = body['formName']
        json_data = body['json']
        pdf_data = body['pdf']
        attachment_archive = body['attachmentArchive']

        licence = self.get_envclassthree_dict()

        if pdf_data:
            attachment_dict = self.get_attachment_dict()
            attachment_dict['file']['data'] = pdf_data + "==="
            attachment_dict['file']['filename'] = "Permis.pdf"
            attachment_dict['title'] = "Pièce jointe principale"
            attachment_dict['file']['content-type'] = "application/pdf"
            licence['__children__'].append(attachment_dict)

        if attachment_archive:
            attachment_dict = self.get_attachment_dict()
            attachment_dict['file']['data'] = attachment_archive['data'] + "==="
            attachment_dict['file']['filename'] = "{}.{}".format("pieces_jointes_formulaire",
                                                                 attachment_archive['archiveType'])
            attachment_dict['title'] = archive_title
            attachment_dict['file']['content-type'] = attachment_archive['archiveMimeType']
            licence['__children__'].append(attachment_dict)

        if json_data:
            envclass3_json_file = base64.b64decode(json_data + "===")
            envclass3_json = json.loads(envclass3_json_file)['dataStore']
            if "etablissement" in envclass3_json:
                if 'description' in envclass3_json['etablissement']:
                    licence['licenceSubject'] = envclass3_json['etablissement']['description']
                if 'rubriques' in envclass3_json['etablissement']:
                    rubrics_list = []
                    for item in envclass3_json['etablissement']['rubriques']['item']:
                        rubrics_list.append(item['numRubrique'])
                    licence['rubrics'] = rubrics_list
                    set_rubrics(self, licence)
                if 'adresse' in envclass3_json['etablissement']:
                    worklocation_dict = self.get_work_locations_dict()
                    worklocation_dict['zipcode'] = envclass3_json['etablissement']['adresse']['cp']
                    worklocation_dict['localite'] = envclass3_json['etablissement']['adresse']['localite']
                    if 'rue' in envclass3_json['etablissement']['adresse']:
                        worklocation_dict['street'] = envclass3_json['etablissement']['adresse']['rue']
                    if 'numero' in envclass3_json['etablissement']['adresse']:
                        worklocation_dict['number'] = envclass3_json['etablissement']['adresse']['numero']
                    if 'boite' in envclass3_json['etablissement']['adresse']:
                        worklocation_dict['number'] += ' {}'.format(envclass3_json['etablissement']['adresse']['boite'])
                    set_location(self, worklocation_dict, licence)
                
                # if 'natura2000' in envclass3_json['etablissement']:
                #     natura2000
                #     if 'site' in envclass3_json['etablissement']:
                #         natura2000Details
                #     if 'ug' in envclass3_json['etablissement']:
                #         natura2000Details
            if "demandeur" in envclass3_json:
                applicant_dict = self.get_applicant_dict()
                if "identification" in envclass3_json["demandeur"]:
                    if "nom" in envclass3_json["demandeur"]["identification"]:
                        applicant_dict['name2'] = envclass3_json["demandeur"]["identification"]['nom']
                    if "prenom" in envclass3_json["demandeur"]["identification"]:
                        applicant_dict['name1'] = envclass3_json["demandeur"]["identification"]['prenom']
                    if "nature" in envclass3_json["demandeur"]["identification"]:
                        if envclass3_json["demandeur"]["identification"]['nature'] == "personneMorale":
                            applicant_dict['@type'] = "Corporation"
                    if "civilite" in envclass3_json["demandeur"]["identification"]:
                        if envclass3_json["demandeur"]["identification"]['civilite'] == "monsieur":
                            applicant_dict['personTitle'] = "mister"
                        elif envclass3_json["demandeur"]["identification"]['civilite'] == "madame":
                            applicant_dict['personTitle'] = "madam"
                if "telecom" in envclass3_json["demandeur"]:
                    if 'tel' in envclass3_json["demandeur"]["telecom"]:
                        applicant_dict['phone'] = envclass3_json["demandeur"]["telecom"]['tel']
                    if 'tel2' in envclass3_json["demandeur"]["telecom"]:
                        applicant_dict['gsm'] = envclass3_json["demandeur"]["telecom"]['tel2']
                    if envclass3_json["demandeur"]["telecom"]['mail']:
                        applicant_dict['email'] = envclass3_json["demandeur"]["telecom"]['mail']
                if "adresse" in envclass3_json["demandeur"]:
                    if 'rue' in envclass3_json["demandeur"]["adresse"]:
                        applicant_dict['street'] = envclass3_json["demandeur"]["adresse"]['rue']
                    if 'numero' in envclass3_json["demandeur"]["adresse"]:
                        applicant_dict['number'] = envclass3_json["demandeur"]["adresse"]['numero']
                    if 'boite' in envclass3_json["demandeur"]["adresse"]:
                        applicant_dict['street'] = "{} {}".format(applicant_dict['street'],
                                                                  envclass3_json["demandeur"]["adresse"]['boite'])
                    if 'cp' in envclass3_json["demandeur"]["adresse"]:
                        applicant_dict['zipcode'] = envclass3_json["demandeur"]["adresse"]['cp']
                    if 'localite' in envclass3_json["demandeur"]["adresse"]:
                        applicant_dict['city'] = envclass3_json["demandeur"]["adresse"]['localite']
                    if 'pays' in envclass3_json["demandeur"]["adresse"]:
                        if envclass3_json["demandeur"]["adresse"]['pays'] != "BE":
                            applicant_dict['localite'] = "{} {}".format(applicant_dict['localite'],
                                                                        envclass3_json["demandeur"]["adresse"]['pays'])
                licence['__children__'].append(applicant_dict)

            if "situation" in envclass3_json:
                if "parcelles" in envclass3_json["situation"]:
                    if "item" in envclass3_json["situation"]["parcelles"]:
                        portionout_list = []
                        for item in envclass3_json["situation"]["parcelles"]['item']:
                            portionout_dict = self.get_parcel_dict()
                            portionout_dict['division'] = item["ins"]["codeDivision"]
                            portionout_dict['section'] = item["ref"]["section"]
                            portionout_dict['radical'] = str(int(item["ref"]["numero"]))
                            portionout_dict['bis'] = item["ref"]["indice"]
                            portionout_dict['exposant'] = item["ref"]["exposant"]
                            portionout_dict['puissance'] = str(int(item["ref"]["diviseur"]))
                            portionout_list.append(portionout_dict)
                            licence['__children__'].append(portionout_dict)

        self.request.set('BODY', json.dumps(licence))
        result = super(AddEsbEnvClassThreePost, self).reply()
        return result

    def get_envclassthree_dict(self):
        return {
            "@type": self.portal_type,
            'portalType': self.portal_type,
            'referenceDGATLP': '',
            'licenceSubject': '',
            'review_state': '',
            'description': '',
            'workLocations': [],
            '__children__': [],
        }

    def get_attachment_dict(self):
        return {
            "@type": "File",
            "title": '',
            "creators": [
                "ESB"
            ],
            "description": "This is a file",
            "file": {
                "data": "",
                "encoding": "base64",
                "filename": "",
                "content-type": ""
            }
        }

    def get_applicant_dict(self):
        return {
            '@type': 'Applicant',
            'personTitle': '',
            'name1': '',
            'name2': '',
            'email': '',
            'phone': '',
            'gsm': '',
            'fax': '',
            'street': '',
            'zipcode': '',
            'city': '',
            'country': '',
        }

    def get_parcel_dict(self):
        return {
            '@type': 'PortionOut',
            'complete_name': '',
            'outdated': '',
            'division': '',
            'section': '',
            'radical': '',
            'bis': '',
            'exposant': '',
            'puissance': '',
        }

    def get_work_locations_dict(self):
        return {
            'number': '',
            'street': '',
            'zipcode': '',
            'localite': '',
        }

