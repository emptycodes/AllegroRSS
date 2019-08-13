from flask import Flask, request, abort
import logging
import yaml
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

def get_authorize_link(client_id, auth_host, auth_port):
    print("""\033[1mFor authorization and generate API Token, click below:\033[0m
    \033[96mhttps://allegro.pl/auth/oauth/authorize?response_type=code&client_id={}&redirect_uri=http://{}:{}&prompt=confirm\033[0m
    """.format(client_id, auth_host, auth_port))

@app.route("/", methods=['GET'])
def get_tokens():
    global settings, secrets, secrets_guardian

    code = request.args.get('code')
    if not code:
        return abort(401)

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
                        "redirect_uri": "http://{}:{}".format(
                            settings["server"]["auth_host"],
                            settings["server"]["auth_port"]
                        )
                    })
    if r.status_code != 200:
        raise exceptions.AuthError("Code has expiration time 10 seconds")
    
    auth_tokens = r.json()

    auth_tokens["authorization"] = auth_token
    auth_tokens["updated"] = int(time.time())

    secrets_guardian.update(auth_tokens)

    func_shutdown = request.environ.get('werkzeug.server.shutdown')
    if func_shutdown is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func_shutdown()

    print("\033[1mEverything has been configured! GLHF!\033[0m")
    return ('Done!', 200)

def generate_api_tokens():
    global secrets_guardian, secrets, settings

    try:
        if secrets["secrets"]["client_id"] == "" or secrets["secrets"]["client_secret"] == "":
            raise exceptions.ConfigError("Make changes in YAML config file and add client ID")
    except TypeError:
        raise exceptions.ConfigError("Config file is empty!")

    get_authorize_link(secrets["secrets"]["client_id"], 
                       settings["server"]["auth_host"], 
                       settings["server"]["auth_port"])

    app.run(host=settings["server"]["auth_host"],
            port=settings["server"]["auth_port"])

if __name__ == "__main__":
    generate_api_tokens()