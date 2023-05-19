from typing import List, Tuple, Iterator

from parsel import Selector

from server.settings import TARGET_URL
from fetcher import Fetcher


class AutoRiaUrlCrawler:

    def __init__(self, proxies: dict):
        self.proxies = proxies
        self.fetch = Fetcher()

    @staticmethod
    def _get_urls_from_page(tree: Selector) -> Tuple[List[str], str | None]:
        link_xpath = "//a[@class='address']/@href"
        next_page_xpath = "//a[@class='page-link js-next ']/@href"

        cars_urls = tree.xpath(link_xpath).getall()
        next_page = tree.xpath(next_page_xpath).get()

        return cars_urls, next_page

    def crawler(self) -> Iterator[str]:
        body = self.fetch.send_request("GET", TARGET_URL, proxies=self.proxies)
        while True:
            items, next_page = self._get_urls_from_page(Selector(body.text))
            for item in items:
                yield item
            if next_page:
                body = self.fetch.send_request("GET", next_page, proxies=self.proxies)
            else:
                break

