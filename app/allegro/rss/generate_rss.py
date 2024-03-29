from rfeed import *
from .description_builder import description_builder, dict_to_html_list


def generate_rss(listing, uri):
    items = []
    for offer in listing.offers:
        items.append(
            Item(
                title=offer.name, link=offer.url, description=description_builder(offer),
                guid=Guid(offer.url)
            )
        )

    category = listing.category
    if category is None:
        category = "Wszystkie kategorie"

    title = "{} w kategorii {}".format(listing.phrase, category)
    feed = rfeed.Feed(
        title=title,
        description=dict_to_html_list(listing.filters),
        link="https://allegro.pl" + uri,
        language="pl-PL",
        items=items,
    )

    return feed
