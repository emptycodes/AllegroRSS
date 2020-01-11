from flask import Flask, request, Response, abort, redirect
from urllib.parse import unquote
import logging
import msgpack
import time
import rfeed
import asyncio
import nest_asyncio
nest_asyncio.apply()

from config import Settings, Secrets
from generate_api_token import get_authorize_link, get_tokens
from refresh_access_token import refresh_access_token
from allegro import search, exceptions

from rss.description_builder import description_builder


application = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

settings = Settings().read()

secrets_guardian = Secrets()
secrets = secrets_guardian.read()

known_searches = {}


def generate_rss(uri):
    global known_searches, secrets_guardian, secrets, settings
    
    loop = asyncio.new_event_loop()
    if not "access_token" in secrets["secrets"]:
        secrets = secrets_guardian.read()
        if not "access_token" in secrets["secrets"]:
            return redirect("/", code=302)

    life_time = secrets["secrets"]["updated"] + secrets["secrets"]["expires_in"]
    if life_time <= time.time():
        auth_host = request.host
        secrets = refresh_access_token(auth_host)

    auth = secrets["secrets"]["access_token"]

    if settings["search"]["cache_file"]:
        try:
            with open("secrets/known_searches.msgp", "rb") as f:
                known_searches = msgpack.unpack(f, raw=False)
        except ValueError:
            known_searches = {}
    
    if not uri in known_searches:
        filters = loop.run_until_complete(
            search.adjust_api_and_web_filters("https://allegro.pl" + uri, auth)
        )

        known_searches[uri] = filters

        if settings["search"]["cache_file"]:
            with open("secrets/known_searches.msgp", "wb") as f:
                msgpack.pack(known_searches, f)

    result = loop.run_until_complete(
                search.search(known_searches[uri]["api"], auth,
                              limit=settings["search"]["search_results_limit"])
            )

    offers = []
    if not settings["search"]["only_regular_offers"]:
        for offer in result["items"]["promoted"]:
            offers.append(offer)
    for offer in result["items"]["regular"]:
        offers.append(offer)

    rss_feed = []
    for offer in offers:
        description = description_builder(uri, known_searches, offer)

        link = "https://allegro.pl/oferta/{}".format(offer["id"])
        if offer.get("vendor"):
            link = offer["vendor"]["url"]

        rss_feed.append(
            rfeed.Item(
                title=offer["name"],
                link=link,
                description=description,
                guid=rfeed.Guid("https://allegro.pl/oferta/{}".format(offer["id"])),
        ))
    
    title = "{} w kategorii {}".format(known_searches[uri]["api"]["phrase"].title(),
                                       known_searches[uri]["humanly"]["category.name"].title())

    feed = rfeed.Feed(
        title = title,
        description = title,
        link = "https://allegro.pl" + uri,
        language = "pl-PL",
        items = rss_feed
    )

    resp = Response(feed.rss())
    resp.headers["Content-Type"] = "text/xml; charset=utf-8"

    return (resp, 200)

@application.route("/", methods=["GET"])
def authorize_oauth():
    global secrets

    code = request.args.get("code")
    if "access_token" in secrets["secrets"]:
        return ("All is perfect configured! GLHF!", 200)

    auth_host = request.host
    if not code:
        allegro_ouath_url = get_authorize_link(
                                secrets["secrets"]["client_id"],
                                auth_host,
                            )
        return redirect(allegro_ouath_url, 302)
    else:
        secrets = get_tokens(code, auth_host)
        
    return ("All is perfect configured! GLHF!", 200)

@application.route("/listing", methods=['GET'])
def listing():
    return generate_rss(request.full_path)

@application.route("/listing/listing.php", methods=['GET'])
def listing_php():
    return generate_rss(request.full_path)

@application.route("/kategoria/<category_id>", methods=['GET'])
def kategoria(category_id):
    return generate_rss(request.full_path)

@application.route("/generateRSS.html", methods=['GET'])
def generaterss_html():
    url = unquote(request.args.get("url"))

    if "https://allegro.pl" in url:
        full_path = url.split("https://allegro.pl")[1]

    else:
        return abort(422)

    return generate_rss(full_path)

if __name__ == "__main__":
    application.run(port=8080)
