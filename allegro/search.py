from allegro.get_web_filters import get_web_filters
from urllib.parse import urlparse, parse_qs

import asyncio
import aiohttp

async def adjust_api_and_web_filters(url, auth):
    url_parsed = urlparse(url)
    query_parsed = parse_qs(url_parsed.query)

    if "kategoria" in url_parsed.path:
        category_id = url_parsed.path.split("/")[2]
    elif "id" in query_parsed:
        category_id = query_parsed["id"][0]
    else:
        category_id = None

    phrase = query_parsed["string"][0]

    loop = asyncio.get_event_loop()
    web_filters, api_search = loop.run_until_complete(
        asyncio.gather(
            get_web_filters(url),
            search({
                "phrase": phrase,
                "category.id": category_id,
            }, auth, limit=1)
        )
    )

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

async def search(filters, auth, limit=60):
    params = {
          # limit in range of 1 to 100
        "limit": limit,
        "sort": "-startTime"
    }

    for key in filters:
        if not filters[key] == None:
            params[key] = filters[key]
    
    params_list = []
    for key, value in params.items():
        if isinstance(value, list):
            for listed_values in value:
                params_list.append([key, listed_values])
        else:
            params_list.append([key, value])

    headers = {
        "Authorization": "Bearer {}".format(auth),
        "accept": "application/vnd.allegro.public.v1+json",
        "content-type": "application/vnd.allegro.public.v1+json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.allegro.pl/offers/listing",
                                params=params_list,
                                headers=headers) as resp:
            if resp.status != 200:
                print(resp.text, resp.status)
            else:
                return await resp.json()