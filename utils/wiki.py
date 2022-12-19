import asyncio
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlencode

import aiohttp

from .api_data import PageData, WikiData, WikiHub
from .errors import PageNotFound, WikiNotFound

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
    
    async def fetch_data(self) -> WikiData:
        """Fetches various information about this wiki from the api."""
        
        try:
            wiki_variables = await self.query_nirvana(controller="MercuryApi", method="getWikiVariables")
        except aiohttp.ContentTypeError as exc:
            raise WikiNotFound from exc

        wiki_id = self.id or wiki_variables["data"]["id"]
        mainpage = wiki_variables["data"]["mainPageTitle"]
        try:
            hub = WikiHub(wiki_variables["data"]["vertical"])
        except ValueError:
            hub = WikiHub.other

        central_wiki = Wiki.from_dot_notation("community", session=self._session)
        tasks = [
            self.query(
                meta="siteinfo",
                siprop="general|statistics",
                prop="revisions",
                rvdir="newer",
                rvlimit=1,
                titles=mainpage
            ),
            central_wiki.query_nirvana(
                controller="WikisApi",
                method="getDetails",
                ids=wiki_id
            )
        ]
        results = await asyncio.gather(*tasks)
        
        return WikiData(
            id=wiki_id,
            name=results[1]["items"][str(wiki_id)]["name"],
            url=self.url or results[1]["items"][str(wiki_id)]["url"],
            description=results[1]["items"][str(wiki_id)]["desc"],
            creation_date=datetime.fromisoformat(list(results[0]["query"]["pages"].values())[0]["revisions"][0]["timestamp"][:-1]),
            hub=hub,
            article_count=results[0]["query"]["statistics"]["articles"],
            page_count=results[0]["query"]["statistics"]["pages"],
            revision_count=results[0]["query"]["statistics"]["edits"],
            image_count=results[0]["query"]["statistics"]["images"],
            post_count=results[1]["items"][str(wiki_id)]["stats"]["discussions"],
            user_count=results[0]["query"]["statistics"]["activeusers"],
            admin_count=results[0]["query"]["statistics"]["admins"]
        )

    async def fetch_page_data(self, name: str) -> PageData:
        """Fetches information about the page on this wiki from the api."""
        
        try:
            data = await self.query_nirvana(
                controller="ArticlesApiController",
                method="getDetails",
                titles=name.replace(" ", "_"),
                abstract=500
            )
        except aiohttp.ContentTypeError as exc:
            raise WikiNotFound from exc

        try:
            data = list(data["items"].values())[0]
        except IndexError:
            raise PageNotFound

        return PageData(
            name=data["title"],
            id=int(data["id"]),
            description=data["abstract"],
            thumbnail=data.get("thumbnail"),
            last_revision_author=data['revision']['user'],
            last_revision_date=datetime.fromtimestamp(int(data['revision']['timestamp'])),
            last_revision_id=data['revision']['id']
        )
    
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
