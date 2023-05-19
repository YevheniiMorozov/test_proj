import logging
import uuid

from django.core.cache import caches
from server.celery import app
from autoria.models import Cars
from autoria.autoria_page_scraper import AutoRiaPageScraper, CarItem
from autoria.autoria_url_crawler import AutoRiaUrlCrawler


logger = logging.getLogger(__name__)


@app.task
def car_page_scraper(url):
    cache = caches['default']
    logger.info(f"In work url {url}")
    crawler = AutoRiaPageScraper({})
    data = crawler.crawler(url)
    cache.set(uuid.uuid4(), data, None)


@app.task
def car_db_worker():
    cars_list = []
    cache = caches['default']

    logger.info("Save data to db")

    keys = list(CarItem.__annotations__.keys())[:-1]

    for key in cache.iter_keys("*"):
        cache_item = cache.get(key)
        if cache_item:
            item = Cars(**cache_item)
            cars_list.append(item)
        cache.delete(key)
    Cars.objects.bulk_update_or_create(cars_list, keys, match_field="url")


@app.task
def manager_task():
    crawler = AutoRiaUrlCrawler({})
    for url in crawler.crawler():
        logger.info(url)
        kwargs = {"url": url}
        car_page_scraper.apply_async(kwargs=kwargs)
