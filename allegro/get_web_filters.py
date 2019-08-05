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
    
    chosen_filters = []
    for slot in data["slots"]:
        for filters in slot["filters"]:
            for filter_value in filters["filterValues"]:
                if filter_value["selected"]:
                    chosen_filter = {
                        "name": filters["name"], 
                        "values": {
                            "name": filter_value["name"],
                        }
                    }

                    if filters["type"] == "NUMERIC" or\
                       filters["type"] == "TEXT" or\
                       filters["type"] == "LOCATION":

                        chosen_filter["values"]["value"] = filter_value["value"]

                    chosen_filters.append(chosen_filter)

    return chosen_filters