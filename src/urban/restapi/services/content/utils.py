
from urban.restapi.exceptions import UndefinedPortalType, DefaultFolderManagerNotFoundError, EnvironmentRubricNotFound
from plone import api
from Products.urban.utils import getLicenceFolder


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
