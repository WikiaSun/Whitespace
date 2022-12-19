from dataclasses import dataclass

from .wiki import Wiki

@dataclass
class Page:
    name: str
    id: int

    wiki: Wiki

    @property
    def url(self):
        return self.wiki.url_to(self.name)
    