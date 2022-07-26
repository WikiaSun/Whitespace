from pathlib import Path
from typing import List

import yaml

class _BotConfigImpl:

    def __init__(self, data):
        self.data = data
    
    def __getattr__(self, name):
        ret = self.data[name]
        
        if type(ret) == dict:
            ret = _BotConfigImpl(ret)

        return ret

    def update(self, new):
        for name, value in new.items():
            if type(value) == dict:
                _BotConfigImpl(self.data[name]).update(value)
            else:
                self.data[name] = value
    
    def __iter__(self):
        for name, value in self.data.items():
            if type(value) == dict:
                yield name, _BotConfigImpl(value)
            else:
                yield name, value

# These are provided to make type checker happy

class BotConfig(_BotConfigImpl):
    default_prefix: str
    description: str
    primary_color: int
    emojis: "BotEmojis"

    credentials: "BotCredentials"
    test_guilds: List[int]
    debug: bool
    cogs: List[str]

class BotCredentials:
    token: str

class BotEmojis:
    success: str
    error: str


with open("config-default.yml") as f:
    config = BotConfig(yaml.safe_load(f))

if Path("config.yml").exists():
    with open("config.yml") as f:
        config.update(yaml.safe_load(f))
