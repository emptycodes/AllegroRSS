from . import timedelta


def dict_to_html_list(elements):
    html_list = "<ul>"
    for key, value in elements.items():
        html_list += "<li><b>{}:</b> {}</li>".format(
                key, value
            )
    html_list += "</ul>"
    return html_list

def description_builder(offer):
    description = ""

    offer_types = {
        "buyNow": "Kup teraz!",
        "auction": "Licytacja",
        "buyNow_auction": "Licytacja i Kup teraz!",
        "advertisement": "Reklama",
    }

    prices = offer.prices
    for price in prices:
        description += "<div><strong>{} {} - {}</strong></div>".format(
            prices[price]["amount"], prices[price]["currency"], offer_types[price]
        )

    if offer.cheapest_delivery:
        if offer.cheapest_delivery["amount"] == 0.00:
            description += "<div>Darmowa dostawa!</div>"
        else:
            description += "<div>{} {} - Najniższa cena dostawy</div>".format(
                str(offer.cheapest_delivery["amount"]),
                offer.cheapest_delivery["currency"],
            )
    else:
        description += "<div>Tylko odbiór osobisty(?)</div>"

    if offer.end_of_offer:
        description += "<div>Kończy się za {}</div>".format(
            timedelta.polish(offer.end_of_offer)
        )

    description += "<div>Ilość dostępnych sztuk: {}</div>".format(offer.quantity)

    description += dict_to_html_list(offer.parameters)

    return description
