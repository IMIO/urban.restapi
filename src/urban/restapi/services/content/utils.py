
from urban.restapi.exceptions import UndefinedPortalType, DefaultFolderManagerNotFoundError, EnvironmentRubricNotFound
from plone import api
from Products.urban.utils import getLicenceFolder


magic_dict = {
    "\x1f\x8b\x08": "gz",
    "\x75\x73\x74\x61\x72": "tar",
    "\x50\x4b\x03\x04": "zip"
    }
magic_max_len = max(len(x) for x in magic_dict)


def set_creation_place(context, data):
    """ """
    portal_type = data.get('@type', None)
    if not portal_type:
        raise UndefinedPortalType
    licence_folder = getLicenceFolder(portal_type)
    context.context = licence_folder
    return data


def set_default_foldermanager(context, data):
    """ """
    if not ('foldermanagers' in data and data['foldermanagers']):
        portal_urban = api.portal.get_tool('portal_urban')
        for licence_config in portal_urban.objectValues('LicenceConfig'):
            if licence_config.id == data.get('@type').lower():
                default_foldermanagers_uids = [foldermanager.UID()
                                               for foldermanager in licence_config.getDefault_foldermanager()]
                data['foldermanagers'] = default_foldermanagers_uids

        if not data['foldermanagers']:
            raise DefaultFolderManagerNotFoundError(["No default foldermanager for this licence type"])
    return data


def set_rubrics(context, data):
    """ """
    rubrics_args = data.get(u'rubrics', '')
    data[u'rubrics'] = []

    if rubrics_args:
        catalog = api.portal.get_tool('portal_catalog')
        rubric_uids = []
        for rubric in rubrics_args:
            rubric_brains = catalog(id=rubric)
            if len(rubric_brains) != 1:
                raise EnvironmentRubricNotFound(rubric)
            rubric_uids.append(rubric_brains[0].UID)
        data[u'rubrics'] = rubric_uids
        return data


def set_location(context, data, licence):
    """ """
    catalog = api.portal.get_tool("portal_catalog")
    if 'street' in data:
        results = catalog(portal_type='Street', Title=str(data['street']))
        if len(results) == 1:
            data['street'] = results[0].getObject().UID()
            licence['workLocations'].append(data)
        else:
            licence['description'] += ("<p>Situation : %s %s %s %s</p>" %
                                       (
                                        str(data['number']),
                                        data['street'],
                                        str(data['zipcode']),
                                        data['localite']
                                       ))


def file_type(filename):
    with open(filename) as f:
        file_start = f.read(magic_max_len)
    for magic, filetype in magic_dict.items():
        if file_start.startswith(magic):
            return filetype
    return "no match"
