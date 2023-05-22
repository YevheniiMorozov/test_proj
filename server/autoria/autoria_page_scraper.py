from typing import Tuple, TypedDict

from parsel import Selector
from retry import retry

from server.settings import NUMBER_API_URL
from autoria.exceptions import ScrappingExceptions
from fetcher import Fetcher


class CarItem(TypedDict):
    title: str | None
    price: int
    mileage: int
    profile_name: str | None
    image_url: str | None
    image_count: int
    car_number: str | None
    phone_number: str | None
    url: str


class AutoRiaPageScraper:

    DATA_HASH_XPATH = "//script/@data-hash"
    CAR_ID_XPATH = "//section[@class='m-padding mb-20 ']/ul/li[2]/span/text()"
    TITLE_XPATH = "//h1[@class='head']/@title"
    FIRST_PATH_XPATH = "//div[@class='price_value']/strong/text()"
    SECOND_PRICE_XPATH = "//div[@class='price_value price_value--additional']/text()"
    MILEAGE_XPATH = "//div[@class='base-information bold']/span[@class='size18']/text()"
    PROFILE_NAME_XPATH = "//div[@class='seller_info_name bold']/text()"
    IMAGE_URL_XPATH = "//div[@id='photosBlock']/div/div/div[1]/picture/source/@srcset"
    CAR_NUMBER_XPATH = "//*[@class='state-num ua']/text()"

    def __init__(self, proxies: dict):
        self.proxies = proxies
        self.fetch = Fetcher()

    def _extract_price(self, tree: Selector) -> int:
        price = tree.xpath(self.FIRST_PATH_XPATH).get()
        if price:
            return int(price.replace(' ', '')[:-1])
        price = tree.xpath(self.SECOND_PRICE_XPATH).get()
        return int(price.replace(' ', '').split("$")[0])

    def _get_id_and_hash(self, tree: Selector) -> Tuple[str, str]:
        """Params for api request, to get phone number"""

        hash_ = tree.xpath(self.DATA_HASH_XPATH).get()
        car_id = tree.xpath(self.CAR_ID_XPATH).get()
        return hash_, car_id

    def _extract_data_from_page(self, tree: Selector) -> CarItem:
        return {
            'title': tree.xpath(self.TITLE_XPATH).get(),
            'price': self._extract_price(tree),
            'mileage': int(tree.xpath(self.MILEAGE_XPATH).get() or 0) * 1000,
            'profile_name': tree.xpath(self.PROFILE_NAME_XPATH).get(),
            'image_url': tree.xpath(self.IMAGE_URL_XPATH).get(),
            'image_count': len(tree.xpath(self.IMAGE_URL_XPATH).getall()),
            'car_number': tree.xpath(self.CAR_NUMBER_XPATH).get(),
            'url': '',
            'phone_number': ''
        }

    def _get_phone_number_from_api(self, hash_, id_) -> str:
        resp = self.fetch.send_request("GET", NUMBER_API_URL.format(car_id=id_, data_hash=hash_), proxies=self.proxies)
        data = resp.json()
        number = data.get('formattedPhoneNumber')
        if number:
            return '38 ' + number

    @staticmethod
    def _check_data(d: CarItem):
        if not (d["title"] and d['price'] and d["phone_number"]):
            raise ScrappingExceptions

    @retry((ScrappingExceptions, AttributeError), tries=20, delay=3)
    def run(self, url: str) -> CarItem | None:
        body = self.fetch.send_request('GET', url, proxies=self.proxies)
        if url.startswith('https://auto.ria.com/uk/newauto'):
            return
        tree = Selector(body.text)
        details = self._extract_data_from_page(tree)
        data_hash, car_id = self._get_id_and_hash(tree)
        number = self._get_phone_number_from_api(data_hash, car_id)
        details.update({
            'phone_number': number,
            'url': url,
        })
        self._check_data(details)
        return details
