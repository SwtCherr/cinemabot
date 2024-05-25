"""googlesearch is a Python library for searching Google, easily."""
import typing as tp
from time import sleep

import aiohttp
from bs4 import BeautifulSoup
from user_agents import get_useragent


async def _req(
        session: aiohttp.ClientSession,
        term: str,
        results: int,
        lang: str,
        start: int,
        proxies: tp.Optional[dict[str, str]],
        timeout: int) -> str:

    async with session.get(
        url="https://www.google.com/search",
        headers={
            "User-Agent": get_useragent()
        },
        params={
            "q": term,
            "num": results + 2,  # Prevents multiple requests
            "hl": lang,
            "start": start,
        },
        # proxies=proxies,
        timeout=timeout,
    ) as resp:
        resp.raise_for_status()
        return await resp.text()


class SearchResult:
    def __init__(self, url: str, title: str, description: str) -> None:
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self) -> str:
        return f"SearchResult(url={self.url}, \
            title={self.title}, description={self.description})"


async def search(
        session: aiohttp.ClientSession,
        term: str,
        num_results: int = 3,
        lang: str = "en",
        proxy: str | None = None,
        sleep_interval: int = 0,
        timeout: int = 5) -> tp.AsyncGenerator[str, None]:

    """
    Search the Google search engine
    """

    escaped_term = term.replace(" ", " ")

    # Proxy
    proxies = None
    if proxy:
        if proxy.startswith("https"):
            proxies = {"https": proxy}
        else:
            proxies = {"http": proxy}

    # Fetch
    start = 0
    while start < num_results:
        # Send request
        resp = await _req(session,
                          escaped_term, num_results - start,
                          lang, start, proxies, timeout)

        # Parse
        soup = BeautifulSoup(resp, "html.parser")
        result_block = soup.find_all("div", attrs={"class": "g"})
        for result in result_block:
            # Find link, title, description
            link = result.find("a", href=True)
            try:
                async with session.get(link) as responce:
                    if responce.status != 200:
                        continue
            except Exception:
                continue
            title = result.find("h3")
            description_box = result.find(
                "div", {"style": "-webkit-line-clamp:2"})
            if description_box:
                description = description_box.text
                if link and title and description:
                    start += 1
                    yield link
        sleep(sleep_interval)
