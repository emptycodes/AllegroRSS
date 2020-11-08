import requests
from urllib.parse import urlparse
import os.path

TRUSTED_PATHS = ["/listing", "/kategoria"]

HEADERS = {"Accept": "application/json"}


class NotTrustedAllegroPath(Exception):
    pass


class AllegroListing:
    def __init__(self, data, uri, limit=10, hide_ads=True):
        self.data = data

        self.phrase = self.data["listing"].get("searchPhrase")
        self.limit = limit
        self.hide_ads = hide_ads
        self.uri = uri

        self.category = self.get_category()
        self.filters = self.get_filters()
        self.offers = self.get_offers()

    def get_offers(self):
        offers = []
        limit = self.limit

        elements = self.data["items-v3-product"]["items"]["elements"]
        for element in elements:
            if element["type"] != "label" or limit:
                if (
                    element["type"] != ["advertisement", "advert_external"]
                    and self.hide_ads
                ):
                    offers.append(AllegroOffer(element))
                    limit -= 1

        return offers

    def get_category(self):
        if "categoryData" in self.data["dfp-dbb"]:
            return self.data["dfp-dbb"]["categoryData"]["name"]

        else:
            return None

    def get_filters(self):
        filters = {}

        if self.data["listing"]["searchMeta"]["appliedFiltersCount"] > 0:
            for filter_ in self.data["chipsAboveFilters"]["filters"]:
                for option in filter_["filters"]:
                    for value in option["filterValues"]:
                        if value["selected"]:
                            filters[option["name"]] = value["name"]

        return filters


class AllegroOffer:
    offer_types = [
        "buyNow",
        "auction",
        "buyNow_auction",
        "advertisement",
        "advert_external",
    ]

    def __init__(self, data):
        self.data = data

        self.name = self.data["name"]
        self.type = self.data["type"]
        self.vendor = self.data["vendor"]
        self.quantity = self.data["quantity"]["value"]
        self.parameters = self.get_parameters()
        self.prices = self.get_prices()
        self.cheapest_delivery = self.get_cheapest_delivery()
        self.end_of_offer = self.get_end_of_offer()
        self.url = self.get_url()

    def get_url(self):
        if self.vendor != "allegro":
            return self.data["url"]

        else:
            return "https://allegro.pl/oferta/" + self.data["id"]

    def get_prices(self):
        prices = {}

        for sellingMode in self.data["sellingMode"]:
            if sellingMode in self.offer_types:
                price = self.data["sellingMode"][sellingMode]["price"]
                prices[sellingMode] = {
                    "amount": float(price["amount"]),
                    "currency": price["currency"],
                }

        return prices

    def get_cheapest_delivery(self):
        cheapest_delivery = {"amount": 0.00, "currency": "PLN"}

        if self.data["shipping"]["freeDelivery"]:
            return cheapest_delivery

        elif "lowest" in self.data["shipping"]:
            cheapest_delivery["amount"] = float(
                self.data["shipping"]["lowest"]["amount"]
            )
            cheapest_delivery["currency"] = self.data["shipping"]["lowest"]["currency"]
            return cheapest_delivery

        #  Only in-person pickup
        return None

    def get_end_of_offer(self):
        if "publication" in self.data:
            return self.data["publication"]["endingTime"]

        else:
            return None

    def get_parameters(self):
        if "parameters" in self.data:
            return self.data["parameters"]

        else:
            return None


def search(path, category, limit, hide_ads):
    parsed_uri = urlparse(path)

    if not os.path.split(parsed_uri.path)[0] in TRUSTED_PATHS:
        raise NotTrustedAllegroPath("Not trusted search possibility path")

    r = requests.get(
        "https://allegro.pl" + path, params={"order": "n"}, headers=HEADERS
    )

    r.raise_for_status()

    return AllegroListing(r.json(), path, limit=limit, hide_ads=hide_ads)
