from flask import Flask, request, abort
import logging
import requests
from base64 import b64encode
import time

from config import Settings, Secrets
from allegro import exceptions

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

settings = Settings().read()

secrets_guardian = Secrets()
secrets = secrets_guardian.read()

URL = "https://allegro.pl/auth/oauth/authorize?response_type=code&client_id={}&redirect_uri=http://{}&prompt=confirm"

def get_authorize_link(client_id, auth_host):
    global URL

    link = URL.format(client_id, auth_host)
    return link

def get_tokens(code, auth_host):
    global settings, secrets, secrets_guardian

    auth_token = b64encode(
                    bytes("{}:{}".format(secrets["secrets"]["client_id"],
                                         secrets["secrets"]["client_secret"]
                                  ), "utf-8")
                 ).decode('utf-8')

    headers = {
        "Authorization": "Basic {}".format(auth_token)
    }

    r = requests.post("https://allegro.pl/auth/oauth/token",
                    headers=headers,
                    params={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": "http://{}".format(auth_host)
                    })
    if r.status_code != 200:
        raise exceptions.AuthError("Code has expiration time 10 seconds")
    
    auth_tokens = r.json()

    auth_tokens["authorization"] = auth_token
    auth_tokens["updated"] = int(time.time())

    return secrets_guardian.update(auth_tokens)