from typing import Callable, Dict
from utils.wiki import Wiki

PrefixCallable = Callable[[str], str]

def wiki_link(url: str, delimiter: str = "_") -> PrefixCallable:
    def get_url(page: str) -> str:
        return url.format(page=page.replace(" ", delimiter))

    return get_url

def internal_wiki_link(link: str) -> str:
    wiki_name, page = link.split(":", 1)
    wiki = Wiki.from_dot_notation(wiki_name)
    return wiki.url_to(page)


PREFIXES: Dict[str, PrefixCallable] = {
    # Fandom
    "w:c":           internal_wiki_link,
    "ww":            wiki_link("https://wikies.fandom.com/wiki/{page}"),
    "w:ru":          wiki_link("https://community.fandom.com/ru/wiki/{page}"),
    "w":             wiki_link("https://community.fandom.com/wiki/{page}"),
    "dev":           wiki_link("https://dev.fandom.com/wiki/{page}"),
    "soap":          wiki_link("https://soap.fandom.com/wiki/{page}"),

    # Wikipedia
    "wp:ru":         wiki_link("https://ru.wikipedia.org/wiki/{page}"),
    "wikipedia:ru":  wiki_link("https://ru.wikipedia.org/wiki/{page}"),
    "wp":            wiki_link("https://en.wikipedia.org/wiki/{page}"),
    "wikipedia":     wiki_link("https://en.wikipedia.org/wiki/{page}"),

    # Wiktionary
    "wiktionary:ru": wiki_link("https://ru.wiktionary.org/wiki/{page}"),
    "wikt:ru":       wiki_link("https://ru.wiktionary.org/wiki/{page}"),
    "wiktionary":    wiki_link("https://en.wiktionary.org/wiki/{page}"),
    "wikt":          wiki_link("https://en.wiktionary.org/wiki/{page}"),

    # Meta and mediawiki
    "m":             wiki_link("https://meta.wikimedia.org/wiki/{page}"),
    "meta":          wiki_link("https://meta.wikimedia.org/wiki/{page}"),
    "mw":            wiki_link("https://mediawiki.org/wiki/{page}"),

    # Other
    "g":             wiki_link("https://google.com/search?q={page}", delimiter="+"),
    "google":        wiki_link("https://google.com/search?q={page}", delimiter="+"),
}