# -*- coding: utf-8 -*-

from eea.faceted.vocabularies.autocomplete import IAutocompleteSuggest
from plone.restapi.services import Service
from zope.component import getMultiAdapter


class SearchAdress(Service):

    portal_type = ""  # to override in subclasses

    def reply(self):
        """
        End point to search street
        callable with 'GET' and '@address'
        Must add minimum one character as query parameters
        You can provide a 'match' parameter to force the exact match on the result
        
        return an object with a list of object compose of uid and name of the street and
            the count of item return
        """

        if not self.request.get("term"):
            raise Exception('Must provide a query parameter with the key "term"')

        self._fix_term("(")
        self._fix_term(")")

        adapter = getMultiAdapter(
            (self.context, self.request),
            IAutocompleteSuggest,
            name="sreets-autocomplete-suggest",
        )

        items = [
            {"name": street["text"], "uid": street["id"]}
            for street in adapter.compute_suggestions(exact_match=self._get_perfect_match())
        ]

        return {"items": items, "items_total": len(items)}

    def _fix_term(self, character):
        term = self.request.get("term")

        if character in term:
            joiner = '"{}"'.format(character)
            term = joiner.join(term.split(character))

        self.request.set("term", term)

        
    def _get_perfect_match(self):
        match = self.request.get("match",False)
        if match:
            return match.lower() in ['true', '1', 't', 'y', 'yes']
        return False