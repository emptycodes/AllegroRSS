import requests
import yaml
from allegro.get_web_filters import get_web_filters
from urllib.parse import urlparse, parse_qs


def adjust_api_and_web_filters(url, auth):
    web_filters = get_web_filters(url)

    url_parsed = urlparse(url)

    if "kategoria" in url_parsed.path:
        """ /kategoria/laptopy-ibm-lenovo-77920
            -> laptopy-ibm-lenovo-77920 """
        category_id = url_parsed.path.split("/")[2]
    else:
        category_id = None

    phrase = parse_qs(url_parsed.query)["string"][0]

    api_search = search({
        "phrase": phrase,
        "category.id": category_id
    }, auth)

    humanly_params = {}
    api_requests_params = {}
    for api_filter in api_search["filters"]:
        for web_filter in web_filters:
            if api_filter["name"] == web_filter["name"]:
                for api_values in api_filter["values"]:
                    if api_values["name"] == web_filter["values"]["name"]:

                        if web_filter["name"] in humanly_params:
                            humanly_params[web_filter["name"]] += ", " +\
                                web_filter["values"]["name"]
                        else:
                            if web_filter["name"] == web_filter["values"]["name"]:
                                humanly_params[web_filter["name"]] =\
                                    web_filter["values"]["value"]
                            else:
                                humanly_params[web_filter["name"]] =\
                                    web_filter["values"]["name"]

                        filter_id = api_filter["id"]
                        if "idSuffix" in api_values:
                            filter_id = filter_id + api_values["idSuffix"]

                            humanly_params[web_filter["name"]] += " " +\
                                web_filter["values"]["value"]
                        
                        if filter_id in api_filter:
                            if type(api_requests_params[filter_id]) is list:
                                api_requests_params[filter_id]

                        if api_filter["type"] in ["NUMERIC", "TEXT", "LOCATION"]:
                            value = web_filter["values"]["value"]
                        else:
                            value = api_values["value"]

                        if filter_id in api_requests_params:
                            if type(filter_id) is list:
                                api_requests_params[filter_id].append(value)
                            else:
                                api_requests_params[filter_id] = \
                                    [api_requests_params[filter_id], value]

                        else:
                            api_requests_params[filter_id] = value
                            

    if "path" in api_search["categories"]:
        category = api_search["categories"]["path"][-1]

        api_requests_params["category.id"] = category["id"]
        humanly_params["category.name"] = category["name"]

    if phrase:
        api_requests_params["phrase"] = phrase

    return {"api": api_requests_params,
            "humanly": humanly_params}

def search(filters, auth, limit=60):
    params = {
          # limit in range of 1 to 100
        "limit": limit,
        "sort": "-startTime"
    }

    for key in filters:
        params[key] = filters[key]

    r = requests.get("https://api.allegro.pl/offers/listing",
                     params=params,
                     headers={
                         "Authorization": "Bearer {}".format(auth),
                         "accept": "application/vnd.allegro.public.v1+json",
                         "content-type": "application/vnd.allegro.public.v1+json"
                     })

    if r.status_code != 200:
        print(r.content, r.status_code)

    return r.json()
