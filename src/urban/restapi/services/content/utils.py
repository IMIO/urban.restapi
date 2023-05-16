# -*- coding: utf-8 -*-

import time

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
        results = catalog(portal_type='Street', Title=str(data['street'].encode('UTF-8')))
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


def quote_parenthesis(s):
    # We need to quote parentheses when searching text indices
    if '(' in s:
        s = s.replace('(', '"("')
    if ')' in s:
        s = s.replace(')', '")"')
    return s


def benchmark_decorator(method):
    def replacement(self, *args, **kwargs):
        # if not self.benchmarking:
        #     return method(self, *args, **kwargs)
        if not self._benchmark.get(method.__name__):
            self._benchmark[method.__name__] = {'counter': 0, 'elapsed_time': 0}
        self._benchmark[method.__name__]['counter'] += 1
        start_time = time.time()
        returned_value = method(self, *args, **kwargs)
        self._benchmark[method.__name__]['elapsed_time'] += time.time() - start_time
        self._benchmark[method.__name__]['average_time'] = \
            self._benchmark[method.__name__]['elapsed_time'] / self._benchmark[method.__name__]['counter']
        return returned_value

    return replacement


def get_config_object(path):
    """
    Get a config object from a path

    :param str path: Path slash separeted from root of portal_urban to the config
    :return: Config object
    :rtype: LicenceConfig
    """
    portal_urban = api.portal.get_tool('portal_urban')

    return portal_urban.restrictedTraverse(path)