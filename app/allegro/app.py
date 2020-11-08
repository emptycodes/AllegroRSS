from flask import Blueprint, request, abort, Response, current_app, redirect
from app.allegro import search, NotTrustedAllegroPath
from app.allegro.rss import generate_rss
from requests.exceptions import HTTPError
from urllib.parse import urlparse

allegro_api = Blueprint("allegro_api", __name__)


@allegro_api.route("/listing", defaults={"category": None})
@allegro_api.route("/listing/listing.php", defaults={"category": None})
@allegro_api.route("/kategoria/<category>")
def get_results(category):
    uri = request.full_path

    ALLEGRORSS_LIMIT_OFFERS = current_app.config["ALLEGRORSS_LIMIT_OFFERS"]
    ALLEGRORSS_HIDE_ADS = current_app.config["ALLEGRORSS_HIDE_ADS"]

    try:
        listing = search(uri, category, ALLEGRORSS_LIMIT_OFFERS, ALLEGRORSS_HIDE_ADS)

    except NotTrustedAllegroPath:
        return abort(400)
    except HTTPError as e:
        return abort(503)

    rss = generate_rss(listing, uri)

    resp = Response(rss.rss())
    resp.headers["Content-Type"] = "text/xml; charset=utf-8"

    return (resp, 200)


@allegro_api.route("/generateRSS.html")
def redirect_from_legacy():
    url = urlparse(request.args.get("url"))

    if url.scheme == "https" and url.netloc == "allegro.pl":
        return redirect(url.path + "?" + url.query)

    else:
        return abort(400)
