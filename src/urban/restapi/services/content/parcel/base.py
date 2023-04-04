# -*- coding: utf-8 -*-

from plone.restapi.services import Service
from Products.urban.browser.searchparcelsview import SearchParcelsView


class SearchParcel(Service):

    portal_type = ""  # to override in subclasses

    def reply(self):
        """
        End point to search cadastral parcel
        callable with 'GET' and '@parcel'
        Must add minimum one query parameters from this list :
            - division
            - section
            - radical
            - bis
            - exposant
            - puissance
            - location
            - street_number
            - parcel_owner

        return an object with a list of serialized parcel object and
            the count of item return
        """
        search = SearchParcelsView(self.context, self.request)
        result = search.search_parcels()

        return {"items": self._serialize_parcel(result), "items_total": len(result)}

    def _serialize_parcel(self, parcels):
        serialized_parcels = []
        for parcel in parcels:
            attributes = self._get_attributes(parcel)
            serialized_parcels.append(
                {attr: getattr(parcel, attr) for attr in attributes}
            )
        return serialized_parcels

    def _get_attributes(self, parcel):
        attributes = dir(parcel)
        return [
            attr
            for attr in attributes
            if not attr.startswith("_") and not callable(getattr(parcel, attr))
        ]
