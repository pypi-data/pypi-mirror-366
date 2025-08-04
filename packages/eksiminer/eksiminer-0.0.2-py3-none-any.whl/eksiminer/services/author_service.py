import time
from bs4 import BeautifulSoup
from slugify import slugify
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Dict, Optional
from .selectors import SELECTORS
from ..core.browser_factory import get_browser_driver
from ..core.schemas import TopicBaseResponse


class AuthorScraper:

    def __init__(
            self,
            driver_name: str = "uc",
            headless: bool = False,
            binary_location: Optional[str] = None,
            version_main: Optional[int] = None
    ):
        self.driver_name = driver_name
        self.headless = headless
        self.browser = get_browser_driver(
            name=driver_name, headless=headless, binary_location=binary_location, version_main=version_main
        )
        self.driver = self.browser.driver
        self.entries = []

    def scrape(self, author: str, number_endless_scroll: int = 10) -> List[Dict[str, str]]:
        """Scrape entries from a specific author's page.

        Args:
            author (str): The author's name.
            number_endless_scroll (int, optional): The number of times to scroll down to load more entries. Defaults to 10.

        Raises:
            e: An error occurred while scraping author entries.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing author entry data.

            [
                {
                    'title': 'fenerbahçe',
                    'content': "1907. entry'm senin adına olsun istedim. “bütün duyguları anlatmaya yetecek kadar kelime yoktur, gerek de yoktur” der cengiz aytmatov . onun yerine bu sevdaya nasıl bulaştığımıza dair bir video bırakayım. çünkü bazen ufak bir enstantane, sayfalarca yazı yazmaktan daha iyi açıklar durumu: link",
                    'date': '02.08.2024 19:19'
                },
                ...
            ]
        """
        author_slug = slugify(author)
        try:
            url = f"https://eksisozluk.com/biri/{author_slug}"
            self.driver.get(url)
            self.scroll_to_bottom()
            self.load_all_entries(number_endless_scroll)
            self.entries = self.parse_entries(author)
            self.entries = [entry.model_dump() for entry in self.entries]
            return self.entries
        except Exception as e:
            print(f"[ERROR] An error occurred while scraping author: {e}")
            raise e
        finally:
            self.browser.quit()

    def scroll_to_bottom(self) -> None:
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    def load_all_entries(self, number_endless_scroll: int) -> None:
        load_more_class = SELECTORS["author"]["load_more"]
        click_count = 0

        while True:
            if number_endless_scroll is not None and click_count >= number_endless_scroll:
                print(
                    f"[INFO] Reached click threshold: {number_endless_scroll}")
                break

            try:
                load_more = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, load_more_class))
                )
                load_more.click()
                time.sleep(2)
                self.scroll_to_bottom()
                click_count += 1
            except:
                break

    def parse_entries(self, author: str) -> List[TopicBaseResponse]:
        topic_class = SELECTORS["author"]["topic"]
        title_class = SELECTORS["author"]["title"]
        content_class = SELECTORS["author"]["content"]
        date_class = SELECTORS["author"]["date"]

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        topics = soup.select(topic_class)
        results = []

        for item in topics:
            title_tag = item.select_one(title_class)
            content_div = item.select_one(content_class)
            date_tag = item.select_one(date_class)

            entry = TopicBaseResponse(
                topic=title_tag.get_text(strip=True) if title_tag else None,
                content=content_div.get_text(
                    separator=" ", strip=True) if content_div else None,
                date=date_tag.get_text(strip=True) if date_tag else None,
                author=author,
            )

            results.append(entry)

        return results
