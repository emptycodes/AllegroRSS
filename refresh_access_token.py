import requests
import json
import yaml

import config
from allegro.exceptions import AuthError


def refresh_access_token():
    config_guardian = config.config()
    secrets_guardian = config.secrets()

    settings = config_guardian.read()
    secrets = secrets_guardian.read()

    r = requests.post("https://allegro.pl/auth/oauth/token",
                    headers={
                        "Authorization": "Basic {}".format(
                                            secrets["secrets"]["authorization"]
                                         )
                    },
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": secrets["secrets"]["refresh_token"],
                        "redirect_uri": "http://{}:{}".format(
                            settings["server"]["auth_host"],
                            settings["server"]["auth_port"]
                        )
                    })
    if r.status_code != 200:
        print(r.json(), r.status_code)
        raise AuthError("Your auth_token or refresh_token is incorrect")
    
    return secrets_guardian.update(r.json())