import requests

from config import Secrets
from allegro.exceptions import AuthError


def refresh_access_token(auth_host):
    secrets_guardian = Secrets()
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
                        "redirect_uri": "http://{}".format(auth_host)
                    })
    if r.status_code != 200:
        raise AuthError("Your auth_token or refresh_token is incorrect")
    
    return secrets_guardian.update(r.json())