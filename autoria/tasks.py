import logging
import uuid
from datetime import date

from django.core.cache import caches

from server.celery import app
from autoria.models import Cars
from autoria.scrapers import AutoRiaPageScraper, CarItem, AutoRiaUrlCrawler
from drivers import SpreadsheetsModule

logger = logging.getLogger(__name__)


@app.task
def car_page_scraper(url):
    cache = caches['default']
    logger.info(f"In work url {url}")
    crawler = AutoRiaPageScraper({})
    data = crawler.run(url)
    cache.set(uuid.uuid4(), data, None)


@app.task
def car_db_saver():
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


@app.task
def spreadsheets_worker():
    cache = caches["sheets"]
    table_name = date.today().strftime("%Y-%m-%d")
    data = []
    for key in cache.iter_keys("*"):
        cache_item = cache.get(key)
        if cache_item:
            data.extend(cache_item)
        cache.delete(key)
    if data:
        m = SpreadsheetsModule(table_name)
        m.add_data_to_table(data)

