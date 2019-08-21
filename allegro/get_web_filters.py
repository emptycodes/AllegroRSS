import asyncio
import aiohttp

async def get_web_filters(link):
    headers = {
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(link, headers=headers) as resp:
            if resp.status != 200:
                print(resp.text, resp.status)
            else:
                data = await resp.json()

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