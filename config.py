from pathlib import Path

import yaml

class BotConfig:

    def __init__(self, data):
        self.data = data
    
    def __getattr__(self, name):
        ret = self.data[name]
        
        if type(ret) == dict:
            ret = BotConfig(ret)

        return ret

    def update(self, new):
        for name, value in new.items():
            if type(value) == dict:
                BotConfig(self.data[name]).update(value)
            else:
                self.data[name] = value
    
    def __iter__(self):
        for name, value in self.data.items():
            if type(value) == dict:
                yield name, BotConfig(value)
            else:
                yield name, value

with open("config-default.yml") as f:
    config = BotConfig(yaml.safe_load(f))

if Path("config.yml").exists():
    with open("config.yml") as f:
        config.update(yaml.safe_load(f))
