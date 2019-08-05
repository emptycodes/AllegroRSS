from flask import Flask, request, Response
import logging
import msgpack
import time
import rfeed

import config
from refresh_access_token import refresh_access_token
from allegro import search

from rss.description_builder import description_builder


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

config_guardian = config.config()
secrets_guardian = config.secrets()

settings = config_guardian.read()
secrets = secrets_guardian.read()


def generate_rss(uri):
    global secrets, settings
    
    life_time = secrets["secrets"]["updated"] + secrets["secrets"]["expires_in"]
    if life_time <= time.time():
        secrets = refresh_access_token()

    auth = secrets["secrets"]["access_token"]

    try:
        with open("known_searches.msgp", "rb") as f:
            known_searches = msgpack.unpack(f, raw=False)
    except ValueError:
        known_searches = {}
    
    if not uri in known_searches:
        filters = search.adjust_api_and_web_filters("https://allegro.pl" + uri, auth)
        known_searches[uri] = filters

        with open("known_searches.msgp", "wb") as f:
            msgpack.pack(known_searches, f)

    result = search.search(known_searches[uri]["api"], auth,
                           limit=settings["search"]["limit"])

    offers = []
    if not settings["search"]["only_regular"]:
        for offer in result["items"]["promoted"]:
            offers.append(offer)
    for offer in result["items"]["regular"]:
        offers.append(offer)

    rss_feed = []
    for offer in offers:
        description = description_builder(uri, known_searches, offer)

        rss_feed.append(
            rfeed.Item(
                title=offer["name"],
                link="https://allegro.pl/oferta/{}".format(offer["id"]),
                description=description,
                guid=rfeed.Guid("https://allegro.pl/oferta/{}".format(offer["id"])),
        ))
    
    title = "{} w kategorii {}".format(known_searches[uri]["api"]["phrase"].title(), 
                known_searches[uri]["humanly"]["category.name"].title())

    feed = rfeed.Feed(
        title = title,
        description = title,  # lazy boi
        link = "https://allegro.pl" + uri,
        language = "pl-PL",
        items = rss_feed
    )

    resp = Response(feed.rss())
    resp.headers["Content-Type"] = "text/xml; charset=utf-8"

    return (resp, 200)

@app.route("/listing", methods=['GET'])
def listing():
    return generate_rss(request.full_path)

@app.route("/kategoria/<category_id>", methods=['GET'])
def kategoria(category_id):
    return generate_rss(request.full_path)

if __name__ == "__main__":
    app.run(host=settings["server"]["rss_host"], 
            port=settings["server"]["rss_port"])
