import requests
from bs4 import BeautifulSoup
import json

def get_web_filters(link):
    r = requests.get(link)
    bs = BeautifulSoup(r.content, 'html.parser')

    scripts = bs.findAll("script", nonce=True)
    for script in scripts:
        if script.text[:34] == "window.__listing_FiltersStoreState":
            data = json.loads(script.text[36:])
    
    chosen_filters = {}
    for slot in data["slots"]:
        for filters in slot["filters"]:
            for filter_value in filters["filterValues"]:
                if filter_value["selected"]:
                    if not filters["type"] in ["NUMERIC", "TEXT", "LOCATION"]:
                        if not filters["name"] in chosen_filters:
                            chosen_filters[filters["name"]] = []
                        chosen_filters[filters["name"]].append(filter_value["name"])

                    else:
                        if not filters["name"] in chosen_filters:
                            chosen_filters[filters["name"]] = {}
                        chosen_filters[filters["name"]][filter_value["name"]] = filter_value["value"]

    return chosen_filters