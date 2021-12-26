from urllib.parse import urlencode
from utils.errors import WikiNotFound

class Wiki:
    def __init__(self, url=None, id=None, *, session):
        if (url is None) and (id is None):
            raise ValueError("You must specify at least one of: id, url")

        self.id = id
        self._session = session

        if url.endswith("/"):
            url = url[:-1]
        self.url = url

    @classmethod
    def from_dot_notation(cls, name, session):
        name = name.split(".")
        if len(name) == 1:
            wiki_url = f"https://{name[0]}.fandom.com"
        elif len(name) == 2:
            wiki_url = f"https://{name[1]}.fandom.com/{name[0]}"
        else:
            raise WikiNotFound
        
        return cls(url=wiki_url, session=session)

    def url_to(self, page, **params):
        """Returns URL to the given page"""

        if not self.url:
            raise RuntimeError("Wiki url is required to do this")
        
        page = page.replace(' ', '_')
        url = f"{self.url}/wiki/{page}"

        if params:
            url += ("?" + urlencode(params))

        return url

    def diff_url(self, revid, oldid=None):
        """Returns URL to the given diff"""
        params = {
            "diff": revid
        }
        if oldid:
            params["oldid"] = oldid
        
        return f"{self.url}/?{urlencode(params)}"
    
    async def query(self, **params):
        """Queries MediaWiki api with given params"""

        if not self.url:
            raise RuntimeError("Wiki url is required to do this")
        
        for key, value in params.items():
            if isinstance(value, bool):
                params[key] = int(value)

        params["action"] = "query"
        params["format"] = "json"
        async with self._session.get(self.url + "/api.php", params=params) as resp:
            return await resp.json()
    
    async def query_nirvana(self, **params):
        """Queries Nirvana with given params"""

        if not self.url:
            raise RuntimeError("Wiki url is required to do this")

        params["format"] = "json"
        async with self._session.get(self.url + "/wikia.php", params=params) as resp:
            return await resp.json()
