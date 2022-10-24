from typing import Any, Optional
from urllib.parse import urlencode

import aiohttp

from utils.errors import WikiNotFound

class Wiki:
    def __init__(self, url: Optional[str] = None, id: Optional[int] = None, *, session: Optional[aiohttp.ClientSession] = None):
        if (url is None) and (id is None):
            raise ValueError("You must specify at least one of: id, url")

        self.id = id
        self._session = session

        if url is not None and url.endswith("/"):
            url = url[:-1]
        self.url = url

    @classmethod
    def from_dot_notation(cls, name: str, session: Optional[aiohttp.ClientSession] = None):
        name_parts = name.split(".")
        if len(name_parts) == 1:
            wiki_url = f"https://{name_parts[0]}.fandom.com"
        elif len(name_parts) == 2:
            wiki_url = f"https://{name_parts[1]}.fandom.com/{name_parts[0]}"
        else:
            raise WikiNotFound
        
        return cls(url=wiki_url, session=session)

    def url_to(self, page: str, **params) -> str:
        """Returns URL to the given page"""

        if not self.url:
            raise RuntimeError("Wiki url is required to do this")
        
        page = page.replace(' ', '_')
        url = f"{self.url}/wiki/{page}"

        if params:
            url += ("?" + urlencode(params))

        return url

    def diff_url(self, revid: int, oldid: Optional[int] = None) -> str:
        """Returns URL to the given diff"""
        params = {
            "diff": revid
        }
        if oldid:
            params["oldid"] = oldid
        
        return f"{self.url}/?{urlencode(params)}"
    
    async def query(self, **params) -> dict[str, Any]:
        """Queries MediaWiki api with given params"""

        if not self.url:
            raise RuntimeError("Wiki url is required to do this")
        if self._session is None:
            raise RuntimeError("This object does not have a session attached to it")
        
        for key, value in params.items():
            if isinstance(value, bool):
                params[key] = int(value)

        params["action"] = "query"
        params["format"] = "json"
        async with self._session.get(self.url + "/api.php", params=params) as resp:
            return await resp.json()
    
    async def query_nirvana(self, **params) -> dict[str, Any]:
        """Queries Nirvana with given params"""

        if not self.url:
            raise RuntimeError("Wiki url is required to do this")
        if self._session is None:
            raise RuntimeError("This object does not have a session attached to it")
        
        params["format"] = "json"
        async with self._session.get(self.url + "/wikia.php", params=params) as resp:
            return await resp.json()
