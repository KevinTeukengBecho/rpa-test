import logging

from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems

from src.business_logic.scrape_cbc_news import ScrapeCBCNews
from src.exceptions.exceptions import MissingArgumentException, InvalidArgumentException

browser = Selenium()

browser_url = "https://www.cbc.ca/"
output_path = "output"


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@task
def search_news():
    """Task to search news."""

    work_items = WorkItems()
    work_items.get_input_work_item()
    payload = work_items.get_work_item_variables()

    search_term = payload.get("search_term")
    search_category = payload.get("search_category")
    number_of_months = payload.get("number_of_months")

    if not search_term:
        logger.error("Search term is missing from input.")
        raise MissingArgumentException("search_term")
    if not search_category:
        logger.error("Search category is missing from input.")
        raise MissingArgumentException("search_category")
    if not number_of_months:
        logger.error("Number of month is missing from input.")
        raise MissingArgumentException("number_of_months")

    try:
        number_of_months = int(number_of_months)
    except ValueError:
        logger.error("Number of month is invalid, please specify a number.")
        raise InvalidArgumentException("number_of_months", number_of_months)

    ScrapeCBCNews(
        browser=browser,
        search_phrase=search_term,
        category=search_category,
        number_of_months=number_of_months,
        news_url=browser_url,
        output_path=output_path,
    ).scrape()
