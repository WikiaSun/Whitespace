"""
This file contains wrapper classes around the data that fandom api sends.
"""

from dataclasses import dataclass
import datetime
import enum

class WikiHub(enum.Enum):
    comics = "comics"
    tv = "tv"
    movies = "movies"
    music = "music"
    books = "books"
    gaming = "gaming"
    lifestyle = "lifestyle"
    travel = "travel"
    creative = "creative"
    toys = "toys"
    education = "education"
    other = "other"

@dataclass
class WikiData:
    name: str
    id: int
    url: str
    description: str
    creation_date: datetime.datetime
    hub: WikiHub
    
    article_count: int
    page_count: int
    image_count: int
    revision_count: int
    post_count: int
    user_count: int
    admin_count: int

    @property
    def wordmark_url(self):
        return f"{self.url}/wiki/Special:FilePath/Wiki-wordmark.png"

    @property
    def favicon_url(self):
        return "https://api.statvoo.com/favicon/?url=" + self.url
