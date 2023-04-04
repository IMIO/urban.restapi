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

        return an object with a list of object compose of uid and name of the street and
            the count of item return
        """
        adapter = getMultiAdapter(
            (self.context, self.request),
            IAutocompleteSuggest,
            name="sreets-autocomplete-suggest",
        )

        items = [
            {"name": street["label"], "uid": street["value"]}
            for street in adapter.compute_suggestions()
        ]

        return {"items": items, "items_total": len(items)}
