import logging
import random

from RPA.Browser.Selenium import Selenium
from selenium.webdriver.chrome.options import Options

from src.business_logic.scrape_utils import save_news_to_excel
from src.dtos.news_item_dto import NewsItemDto
from src.exceptions.exceptions import ScrapeException

logger = logging.getLogger(__name__)


class ScrapeNews:
    news_items: list[NewsItemDto] = []
    can_navigate_to_next_page = True

    def __init__(
        self,
        browser: Selenium,
        search_phrase: str,
        number_of_months: int,
        news_url: str,
        category: str,
        output_path: str,
    ):
        self.browser = browser
        self.search_phrase = search_phrase
        self.category = category
        self.number_of_months = number_of_months
        self.news_url = news_url
        self.output_path = output_path

    def scrape(self) -> None:
        """Scrapes a news website"""
        try:
            self.open_browser()
            self.enter_search_phrase()
            self.verify_search_results()
            self.select_category_if_exists()
            self.sort_search_results_by_latest()
            self.extract_news_items()
            while self.can_navigate_to_next_page:
                self.navigate_to_next_page()
                self.extract_news_items()
        except ScrapeException as e:
            logger.error(e.message)
            raise
        except Exception as e:
            logger.error("An unexpected error occurred", e)
            raise
        finally:
            if self.news_items:
                logger.info("Writing scraped news to excel document")
                save_news_to_excel(
                    "search_results",
                    self.output_path,
                    self.news_items,
                    self.search_phrase,
                )

    def open_browser(self) -> None:
        """Open a browser and navigate to the news URL."""
        logger.info("Opening browser on URL %s", self.news_url)

        # CBC picks up bot. This is to scrape in stealth mode.
        browser_options = Options()
        browser_options.add_argument(
            f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
            f"{random.randint(90, 110)}.0.{random.randint(1000, 9999)}.124 Safari/537.36"
        )

        self.browser.open_available_browser(
            self.news_url,
            headless=True,
            maximized=True,
            options=browser_options,
            browser_selection="chrome",
        )
        logger.info("Successfully opened browser on URL %s", self.news_url)

    def enter_search_phrase(self) -> None:
        """Specify and search for the search_phrase."""
        raise NotImplementedError("Please implement enter search phrase.")

    def verify_search_results(self) -> None:
        """Verify the search returned any results."""
        pass

    def select_category_if_exists(self) -> None:
        """Select the category if it exists for the news website."""
        pass

    def sort_search_results_by_latest(self) -> None:
        """Sorts the search results by latest."""
        raise NotImplementedError("Please implement sort search results.")

    def extract_news_items(self) -> None:
        """Extract the news items."""
        raise NotImplementedError("Please implement extract news items.")

    def navigate_to_next_page(self) -> None:
        """Navigates to next search result page."""
        raise NotImplementedError("Please implement navigate to next page.")
