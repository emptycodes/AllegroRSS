from rfeed import *
from .description_builder import description_builder


def generate_rss(listing, uri):
    items = []
    for offer in listing.offers:
        items.append(
            Item(
                title=offer.name, link=offer.url, description=description_builder(offer)
            )
        )

    category = listing.category
    if category is None:
        category = "Wszystkie kategorie"

    title = "{} w kategorii {}".format(listing.phrase, category)
    feed = rfeed.Feed(
        title=title,
        description=str(listing.filters),
        link="https://allegro.pl" + uri,
        language="pl-PL",
        items=items,
    )

    return feed
