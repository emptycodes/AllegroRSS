from rss import timedelta_pl

def description_builder(uri, known_searches, offer):
    description = ""
    
    if offer["sellingMode"]["format"] == "BUY_NOW":
            offer_type = "Kup teraz!"
    else:
        offer_type = "Licytacja"

    if "fixedPrice" in offer["sellingMode"]:
        price = offer["sellingMode"]["price"]["amount"]
        fixed_price = offer["sellingMode"]["fixedPrice"]["amount"]

        if price != fixed_price:
            offer_type = "Licytacja z możliwością Kup teraz!"

    description += "<div><strong>{} {} - {}</strong></div>".format(
        offer["sellingMode"]["price"]["amount"],
        offer["sellingMode"]["price"]["currency"],
        offer_type
    )

    if "amount" in offer["delivery"]["lowestPrice"]:
        if offer["delivery"]["lowestPrice"]["amount"] == "0.00":
            description += "<div>Darmowa dostawa!</div>"
        else:
            description += "<div>{} {} - Najniższa cena dostawy</div>".format(
                offer["delivery"]["lowestPrice"]["amount"],
                offer["delivery"]["lowestPrice"]["currency"],
            )
    else:
        description += "<div>Tylko odbiór osobisty(?)</div>"

    if "publication" in offer:
        description += "<div>Kończy się za {}</div>".format(
            timedelta_pl.timedelta_pl(offer["publication"]["endingAt"])
        )

    description += "<div>Ilość dostępnych sztuk: {}</div>".format(
        offer["stock"]["available"]
    )

    description += "<ul>"  # is this good?
    for filter_list in known_searches[uri]["humanly"]:
        if not filter_list == "category.name":
            description += "<li><b>{}</b>: {}</li>".format(
                filter_list.title(),
                known_searches[uri]["humanly"][filter_list].title()
            )
    description += "</ul>"

    return description