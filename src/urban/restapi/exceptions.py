# -*- coding: utf-8 -*-

from plone.restapi.exceptions import APIError


class UrbanRestAPIError(APIError):
    """ Base class for urban rest api errors"""


class UndefinedPortalType(UrbanRestAPIError):
    """
    Raised when no portal_type defined.
    """


class EnvironmentRubricNotFound(UrbanRestAPIError):
    """
    Raised when no corresponding environment rubric is found
    in urban.
    """


class DefaultFolderManagerNotFoundError(UrbanRestAPIError):
    """
    Raised when no default foldermanager for this licence type is found
    in urban.
    """
