import time
from typing import List, Dict, Optional
from .topic_service import TopicScraper


class TopicUrlService(TopicScraper):

    def scrape(self, urls: List[str], max_page_limit: Optional[int] = None, reverse: bool = False) -> List[Dict[str, str]]:
        """Scrape topics from a list of URLs.

        Args:
            urls (List[str]): A list of URLs to scrape.
            max_page_limit (Optional[int], optional): The maximum number of pages to scrape for each URL. Defaults to None.
            reverse (bool, optional): Whether to reverse the order of scraping. Defaults to False.

        Raises:
            e: An error occurred during scraping.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing topic data.

            [
                {
                    'content': 'Example content',
                    'author': 'Example Author',
                    'date': '01.01.2023 12:00 ~ 13:00',
                    'topic': 'yeliz kod adlı akpli ahmet hamdi çamlı',
                },
                ...
            ]
        """
        try:
            for url in urls:
                self.scrape_url(url, max_page_limit, reverse)

            self.browser.quit()

            self.entries = [entry.model_dump() for entry in self.entries]
            return self.entries

        except Exception as e:
            if self.verbose:
                print(f"[ERROR] An error occurred during scraping: {e}")

            if self.retry < 3:
                self.retry += 1
                if self.verbose:
                    print(f"[INFO] Retrying... Attempt {self.retry}/3")
            else:
                print("[ERROR] Max retries reached. Exiting.")
                raise e

            self.restart_driver()
            self.scrape(urls, max_page_limit, reverse)

        finally:
            self.browser.quit()

    def scrape_url(self, url: str, max_page_limit: Optional[int] = None, reverse: bool = False) -> None:
        if "?day" in url:
            url = url.split("?day")[0]

        if "?a=popular" in url:
            url = url.split("?a=popular")[0]

        self.driver.get(url)
        time.sleep(2)

        self.topic_url = self.driver.current_url

        total_pages = self.get_total_pages()

        if max_page_limit is not None:
            page_count = min(max_page_limit, total_pages)
        else:
            page_count = total_pages

        if reverse:
            page_range = range(
                total_pages, total_pages - page_count, -1)
        else:
            page_range = range(1, page_count + 1)

        for page in page_range:
            page_entries = self.scrape_page(page, url)

            self.entries.extend(page_entries)

        return
