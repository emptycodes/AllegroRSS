from rss import timedelta_pl

def description_builder(uri, known_searches, offer):
    description = ""

    offer_type = {
        "BUY_NOW": {"name": "Kup teraz!",
                    "state": False},
        "AUCTION": {"name": "Licytacja",
                    "state": False},
        "ADVERTISEMENT": {"name": "Reklama",
                          "state": False}
    }

    for selling_mode in offer_type:
        offer_type[selling_mode]["state"] =\
            offer["sellingMode"]["format"] == selling_mode

    if "fixedPrice" in offer["sellingMode"]:
        price = offer["sellingMode"]["price"]["amount"]
        fixed_price = offer["sellingMode"]["fixedPrice"]["amount"]

        if price != fixed_price:
            offer_type["AUCTION"]["state"] = True

    if offer_type["BUY_NOW"]["state"] and offer_type["AUCTION"]["state"]:
        description += "<div><strong>{} {} - {}</strong></div>".format(
            offer["sellingMode"]["price"]["amount"],
            offer["sellingMode"]["price"]["currency"],
            offer_type["AUCTION"]["name"]
        )

        description += "<div><strong>{} {} - {}</strong></div>".format(
            offer["sellingMode"]["fixedPrice"]["amount"],
            offer["sellingMode"]["fixedPrice"]["currency"],
            offer_type["BUY_NOW"]["name"]
        )

    else:
        for selling_mode in offer_type:
            if offer_type[selling_mode]["state"] == True:
                offer_type_name = offer_type[selling_mode]["name"]

        description += "<div><strong>{} {} - {}</strong></div>".format(
            offer["sellingMode"]["price"]["amount"],
            offer["sellingMode"]["price"]["currency"],
            offer_type_name
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