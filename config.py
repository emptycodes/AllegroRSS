import yaml

class config():
    def read(self):
        with open("config.yaml", "r") as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)
    
        return config

class secrets():
    def read(self):
        with open("secrets.yaml", "r") as f:
            try:
                secrets = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)
        
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