from typing import Optional, Match
from utils.wiki import Wiki
from .prefixes import PREFIXES

class Link:
    def __init__(self, match: Match[str], wiki: Wiki) -> None:
        self.target: str = match.group(1)
        self.title: Optional[str] = match.group(2)

        if self.title == "":
            self.title = self.target.split(":")[-1]
        if self.title is None:
            self.title = self.target

        self.wiki = wiki
        self.original = match.group(0)
        self.url = self.make_url()
    
    def make_url(self) -> str:
        for prefix, func in PREFIXES.items():
            if self.target.startswith(prefix):
                return func(self.target[len(prefix) + 1:])

        return self.wiki.url_to(self.target)

    def __repr__(self):
        return f"<Link target={self.target} title={self.title} url={self.url}>"

    def to_hyperlink(self) -> str:
        return f"[{self.title}](<{self.url}>)"

    def to_link(self) -> str:
        return f"<{self.url}>"