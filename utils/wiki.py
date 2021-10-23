from urllib.parse import urlencode

class Wiki:
    def __init__(self, url=None, id=None, *, session):
        if (url is None) and (id is None):
            raise ValueError("You must specify at least one of: id, url")

        self.url = url
        self.id = id
        self._session = session

    def url_to(self, page, **params):
        """Returns URL to the given page"""

        if not self.url:
            raise RuntimeError("Wiki url is required to do this")
        
        page = page.replace(' ', '_')
        url = f"{self.url}/wiki/{page}"

        if params:
            url += ("?" + urlencode(params))

        return url
    
    async def query(self, **params):
        """Queries MediaWiki api with given params"""

        if not self.url:
            raise RuntimeError("Wiki url is required to do this")

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
