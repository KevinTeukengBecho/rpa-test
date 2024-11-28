import copy
import logging
import time
from datetime import date, datetime

from selenium.common import NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys

from src.business_logic.scrape_news import ScrapeNews
from src.business_logic.scrape_utils import download_image
from src.dtos.news_item_dto import NewsItemDto
from src.exceptions.exceptions import (NewsCategoryNotFoundException,
                                       ScrapeException,
                                       SearchPhraseContainsNoResultsException,
                                       UnexpectedEndOfNavigationException)

logger = logging.getLogger(__name__)


class ScrapeCBCNews(ScrapeNews):

    last_news_extracted_index: int = 0

    def enter_search_phrase(self):
        """Specify and search for the search_phrase."""
        try:
            """Specify and search for the search_phrase."""
            search_button_locator = "id:searchButton"
            search_input_text_locator = "id:gn-compact-search"

            self._accept_cookies_if_present()

            self.browser.click_element_when_visible(search_button_locator)
            # self.browser.click_element(search_button_locator)
            # self.browser.execute_javascript('document.getElementById("searchButton").click();')
            self.browser.input_text(search_input_text_locator, self.search_phrase)
            self.browser.press_keys(search_input_text_locator, Keys.RETURN)
            logger.info(
                "Successfully submitted a search for phrase '%s'", self.search_phrase
            )
        except Exception as exc:
            logger.exception("an error occured", exc)
            self.browser.capture_page_screenshot("screenshot.png")
            raise ScrapeException(
                f"Failed to search phrase {self.search_phrase}"
            ) from exc

    def verify_search_results(self):
        """Verify the search returned any results.

        Throws: SearchPhraseContainsNoResultsException if search does not contain any results
        """
        news_results_item_xpath = "class:contentListWrapper"

        try:
            self.browser.wait_until_element_is_visible(
                news_results_item_xpath, timeout=15
            )
            logger.info("Search phrase '%s' contains results.", self.search_phrase)
        except AssertionError:
            raise SearchPhraseContainsNoResultsException(
                f"Search phrase '{self.search_phrase}' does not contain any results"
            )

    def select_category_if_exists(self):
        """Select the category if it exists for the news website."""
        see_all_categories_selector = "id:searchFilterSelect"
        logger.info("Looking for news category %s", self.category)
        try:
            self.browser.select_from_list_by_label(
                see_all_categories_selector, self.category
            )
            time.sleep(3)
            logger.info("Successfully selected news category %s", self.category)
        except NoSuchElementException:
            raise NewsCategoryNotFoundException(self.category)

    def sort_search_results_by_latest(self):
        """Sorts the search results by latest."""
        try:
            sort_locator = "id:sortOrderSelect"
            self.browser.select_from_list_by_label(sort_locator, "Most recent")
            # Wait before extracting to give time to the page to refresh and re-arrange the news items.
            time.sleep(3)
        except WebDriverException:
            raise ScrapeException("Failed to sort news by latest.")

    def extract_news_items(self):
        """Extract the news items."""
        news_items_parent_locator = "class:contentListCards"

        self.browser.wait_until_element_is_visible(news_items_parent_locator, timeout=5)
        news_items_parent_element = self.browser.get_webelement(
            news_items_parent_locator
        )
        news_count = len(self.browser.find_elements("tag:a", news_items_parent_element))

        start_extract_index = copy.deepcopy(self.last_news_extracted_index)

        for index in range(start_extract_index, news_count):
            try:
                logger.info(
                    "processing news item number %s", self.last_news_extracted_index + 1
                )
                news_items_elements = self.browser.find_elements(
                    "tag:a", news_items_parent_element
                )
                news_item = news_items_elements[index]
                self.browser.scroll_element_into_view(news_item)

                timestamp = self.browser.get_element_attribute(
                    self.browser.find_element("class:timeStamp", news_item), "datetime"
                )
                news_date = (
                    datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
                ).date()
                if not self._can_save_news(news_date):
                    logger.info(
                        "Stopping processing. We have reached allowed month to scrape limit."
                    )
                    self.can_navigate_to_next_page = False
                    break

                title = self.browser.get_text(
                    self.browser.find_element("class:headline", news_item)
                )
                description = self.browser.get_text(
                    self.browser.find_element("class:description", news_item)
                )

                image_div_element = self.browser.find_element(
                    "class:imageMedia", news_item
                )
                image_url = self.browser.get_element_attribute(
                    self.browser.find_element("tag:img", image_div_element), "src"
                )
                image_name = download_image(image_url, f"{self.output_path}", title)

                logger.info("news item with title %s successfully extracted", title)
                self.news_items.append(
                    NewsItemDto(
                        title=title,
                        description=description,
                        date=news_date,
                        image_name=image_name,
                    )
                )
            except WebDriverException:
                raise ScrapeException("Error extracting a news item.")
            finally:
                self.last_news_extracted_index += 1

    def _can_save_news(self, current_news_date: date):
        """Verifies whether the news can be saved based on the news date and the number of months to seek data for."""
        current_date = datetime.now().date()
        years_diff = current_date.year - current_news_date.year
        fixed_months_diff = current_date.month - current_news_date.month

        months_diff = years_diff * 12 + fixed_months_diff
        if months_diff < (self.number_of_months or 1):
            return True
        return False

    def navigate_to_next_page(self):
        """Navigates to next search result page."""
        try:
            search_button_locator = "class:loadMore"
            self.browser.scroll_element_into_view(
                self.browser.find_element(search_button_locator)
            )
            self.browser.click_element_when_visible(search_button_locator)
            logger.info("Loading more news...")
        except WebDriverException:
            raise UnexpectedEndOfNavigationException()

    def _accept_cookies_if_present(self):
        """Accepts the cookies if present on the CBC news site."""
        try:
            accept_cookies_locator = "id:didomi-notice-agree-button"
            # self.browser.wait_until_element_is_visible(accept_cookies_locator, timeout=15)
            self.browser.click_element_when_visible(accept_cookies_locator)
            # self.browser.click_element(accept_cookies_locator)
            # self.browser.execute_javascript('document.getElementById("didomi-notice-agree-button").click();')
            time.sleep(3)
        except Exception as exc:
            logger.warn("Failed to accept cookies.", exc)
