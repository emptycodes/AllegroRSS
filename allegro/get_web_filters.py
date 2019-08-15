import requests


def get_web_filters(link):
    r = requests.get(link, headers={
        "Accept": "application/json"
    })

    data = r.json()

    chosen_filters = {}
    for filters in data["listing"]["filters"]:
        filters_type = filters["filters"][0]["type"]
        for option in filters["filters"][0]['filterValues']:
            if option["selected"]:
                if not filters_type in ["NUMERIC", "TEXT", "LOCATION"]:
                    if not filters["name"] in chosen_filters:
                        chosen_filters[filters["name"]] = []
                    chosen_filters[filters["name"]].append(option["name"])

                else:
                    if not filters["name"] in chosen_filters:
                        chosen_filters[filters["name"]] = {}
                    chosen_filters[filters["name"]][option["name"]] = option["value"]

    return chosen_filters