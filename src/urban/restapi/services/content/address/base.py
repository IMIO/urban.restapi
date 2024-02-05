# -*- coding: utf-8 -*-

from eea.faceted.vocabularies.autocomplete import IAutocompleteSuggest
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from plone import api

class SearchAdress(Service):

    portal_type = ""  # to override in subclasses

    def search_term(self):
        if not self.request.get("term"):
            return None

        self._fix_term("(")
        self._fix_term(")")

        adapter = getMultiAdapter(
            (self.context, self.request),
            IAutocompleteSuggest,
            name="sreets-autocomplete-suggest",
        )

        items = [
            {"name": street["text"], "uid": street["id"]}
            for street in adapter.compute_suggestions(
                exact_match=self._get_bool_parameter("match"),
                include_disable=self._get_bool_parameter("include_disable")
            )
        ]

        return items
        
    def street_code(self):
        street_code = self.request.get("street_code", None)
        if not street_code:
            return None

        items = [
            {"name": street.Title, "uid": street.UID}
            for street in api.content.find(getStreetCode= [int(street_code)])
        ]

        return items


    def reply(self):
        """
        End point to search street
        callable with 'GET' and '@address'
        Must add minimum one character as query parameters with the "term" key 
        or the street code with the "street_code" key
        You can provide a 'match' parameter to force the exact match on the result
        You can provide a 'include_disable' parameter to expand search in disable streets

        return an object with a list of object compose of uid and name of the street and
            the count of item return
        """

        street_term = self.search_term()
        street_code = self.street_code()

        if street_term is None and street_code is None:
            raise Exception(
                'Must provide at least one query parameter '
                'with either the key "term" or "street_code"'
            )

        return {
            "items": street_code or street_term,
            "items_total": len(street_code or street_term)
        }

    def _fix_term(self, character):
        term = self.request.get("term")

        if character in term:
            joiner = '"{}"'.format(character)
            term = joiner.join(term.split(character))

        self.request.set("term", term)

    def _get_bool_parameter(self, parameter):
        match = self.request.get(parameter, False)
        if match:
            return match.lower() in ['true', '1', 't', 'y', 'yes']
        return False
