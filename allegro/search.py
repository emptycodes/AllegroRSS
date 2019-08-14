import requests
from allegro.get_web_filters import get_web_filters
from urllib.parse import urlparse, parse_qs


def adjust_api_and_web_filters(url, auth):
    web_filters = get_web_filters(url)

    url_parsed = urlparse(url)

    if "kategoria" in url_parsed.path:
        category_id = url_parsed.path.split("/")[2]
    else:
        category_id = None

    phrase = parse_qs(url_parsed.query)["string"][0]

    api_search = search({
        "phrase": phrase,
        "category.id": category_id,
    }, auth, limit=1)

    result = {
        "api": {},
        "humanly": {}
    }

    web_filters_list = [web_filter for web_filter in web_filters]
    for api_filter in api_search["filters"]:
        if api_filter["name"] in web_filters_list:

            value = None
            if isinstance(web_filters[api_filter["name"]], dict):
                for api_value in api_filter["values"]:
                    name = api_value["name"]

                    if name in web_filters[api_filter["name"]]:
                        key = api_filter["id"] + api_value["idSuffix"]
                        value = web_filters[api_filter["name"]][name]

                        result["api"][key] = value
                        
                        if not api_filter["name"] in result["humanly"]:
                            result["humanly"][api_filter["name"]] =\
                                "{} {}".format(name, value)
                        else:
                            result["humanly"][api_filter["name"]] +=\
                                ", {} {}".format(name, value)
            else:
                key = api_filter["id"]
            
            if not value:
                if api_filter in ["NUMERIC", "TEXT", "LOCATION"]:
                    value = web_filters[api_filter["name"]][0]
                    result["humanly"][api_filter["name"]] = value

                else:
                    values = []
                    for api_value in api_filter["values"]:
                        name = api_value["name"]
                        if name in web_filters[api_filter["name"]]:
                            values.append(api_value["value"])

                            if not api_filter["name"] in result["humanly"]:
                                result["humanly"][api_filter["name"]] = name
                            else:
                                result["humanly"][api_filter["name"]] +=\
                                    ", " + name
                    
                result["api"][key] = values

    if "path" in api_search["categories"]:
        category = api_search["categories"]["path"][-1]

        result["api"]["category.id"] = category["id"]
        result["humanly"]["category.name"] = category["name"]

    if phrase:
        result["api"]["phrase"] = phrase

    return result

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