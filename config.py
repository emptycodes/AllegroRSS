import yaml
import os

from allegro import exceptions

def load_env_vars(config_dict):
    for var_name in config_dict:
        env_var = os.environ.get(var_name.upper())

        if env_var != None:
            if isinstance(config_dict[var_name], bool):
                if env_var.upper() == "TRUE":
                    env_var = True
                
                elif env_var.upper() == "FALSE":
                    env_var = False
                
                elif env_var.isdigit() != False:
                    if int(env_var) == 0:
                        env_var = False
                    else:
                        env_var = True

            else:
                if env_var.isdigit() != False:
                    env_var = int(env_var)
            
            config_dict[var_name] = env_var
  
    return config_dict

class Settings():
    def read(self):
        with open("config.yaml", "r") as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)

        for headers in config:
            config[headers] = load_env_vars(config[headers])

        with open("config.yaml", "w") as f:
            try:
                yaml.dump(config, f)
            except yaml.YAMLError as exc:
                print(exc)

        return config

class Secrets():
    @classmethod
    def read(self):
        with open("secrets.yaml", "r") as f:
            try:
                secrets = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)
        
        important_vars = {"client_id": None,
                          "client_secret": None}

        loaded_env_vars = load_env_vars(important_vars)
        for loaded_env_var in loaded_env_vars:
            if loaded_env_vars[loaded_env_var] != None:
                secrets["secrets"][loaded_env_var] =\
                    loaded_env_vars[loaded_env_var]

        if not secrets["secrets"]["client_id"] and\
           not secrets["secrets"]["client_secret"]:

            exceptions.SecretsError("You forgot about clients ID and secret!")

        return secrets

    def update(self, refreshed_tokens):
        secrets = self.read()
        for key in refreshed_tokens:
            secrets["secrets"][key] = refreshed_tokens[key]

        with open("secrets.yaml", "w") as f:
            try:
                yaml.dump(secrets, f)
            except yaml.YAMLError as exc:
                print(exc)

        return secrets