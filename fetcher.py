import logging
from requests import request


logger = logging.getLogger("Fetcher")


class Fetcher:

    DEFAULT_HEADERS = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'accept-encoding': 'gzip',
        'content-type': 'application/json; charset=utf-8',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0'
    }

    ALLOW_STATUS_CODE = [200]
    RETRIES = 10
    ALLOW_HTTP_METHODS = ['GET', 'POST', 'PUT', "DELETE"]

    def send_request(self, method: str, url: str, headers: dict = None, proxies: dict = None,
                     retries: int = None, allow_status_codes: list = None):

        if method is None or method.upper() not in self.ALLOW_HTTP_METHODS:
            raise Exception('HTTP method is required')

        if allow_status_codes is None:
            allow_status_codes = self.ALLOW_STATUS_CODE

        if retries is None:
            retries = self.RETRIES

        if headers is None:
            headers = self.DEFAULT_HEADERS

        retrie_counter = 0

        while retrie_counter < retries:
            try:
                logger.info(f"Send requests to {url}")
                response = request(method=method, url=url, headers=headers, proxies=proxies, timeout=32)
            except Exception as e:
                logger.error(e)
                retrie_counter += 1
                continue

            if response.status_code in allow_status_codes:
                return response

            retrie_counter += 1
