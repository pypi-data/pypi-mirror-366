import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .selectors import SELECTORS
from ..core.browser_factory import get_browser_driver
from ..core.schemas import TopicBaseResponse


class TopicScraper:

    def __init__(
            self,
            driver_name: str = "uc",
            headless: bool = False,
            binary_location: Optional[str] = None,
            version_main: Optional[int] = None,
            verbose: bool = False
    ):
        self.driver_name = driver_name
        self.headless = headless
        self.binary_location = binary_location
        self.version_main = version_main
        self.verbose = verbose
        self.browser = get_browser_driver(
            name=self.driver_name,
            headless=self.headless,
            binary_location=self.binary_location,
            version_main=self.version_main
        )
        self.driver = self.browser.driver
        self.entries = []
        self.topic_url = ""
        self.retry = 0

    def scrape(self, topic: str, max_page_limit: Optional[int] = None, reverse: bool = False) -> List[Dict[str, str]]:
        """Scrape entries for a given topic.

        Args:
            topic (str): The topic to search for.
            max_page_limit (Optional[int], optional): The maximum number of pages to scrape. Defaults to None.
            reverse (bool, optional): Whether to scrape pages in reverse order. Defaults to False.

        Raises:
            e: An error occurred during scraping.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the scraped entry data.

            [
                {
                    'content': 'hobileri arasında yeliz kod adlı akpli ahmet hamdi çamlı dan alıntı yapmak bulunan, alıntı yapmayı çok seven şahıs. kendisinin diplomasının sahte olduğu gibi, karısının da yüksek lisans diploması çalıntı çıkmış. karı-koca karakterleri uyumlu bir evlilik yapmışlar. di\'nin diploması çalıntıdır bir tarafta sahte diplomalı futbolcular, diğer tarafta sahte diplomalı müteahhitler. neden bu iki rezil şıktan birini seçiyoruz diye sorgulamak yerine, adice, ahlaksızca kendisini savunacak yaratıklar bulunacaktır. gerizekalı şerefsizlerden duyabileceğiniz argümanlar: "bizim tarafın sahte diplomalılarını desteklemiyorsanız, karşı tarafa çalışıyorsunuz, gerçek atatürkçü, rozet takar, dövme yaptırır ve oklu partinin sahte diplomalılarını destekler..."',
                    'author': 'hiperaktf c',
                    'date': '29.07.2025 13:32 ~ 15:51',
                    'topic': 'yeliz kod adlı akpli ahmet hamdi çamlı',
                },
                ...
            ]
        """
        try:
            self.open_search_page()
            self.submit_search(topic)
            total_pages = self.get_total_pages()

            if max_page_limit is not None:
                page_count = min(max_page_limit, total_pages)
            else:
                page_count = total_pages

            if reverse:
                page_range = range(total_pages, total_pages - page_count, -1)
            else:
                page_range = range(1, page_count + 1)

            if self.verbose:
                print(
                    f"[INFO] Scraping topic: {self.topic_url} with {len(page_range)} pages")

            for page in page_range:
                page_entries = self.scrape_page(page, topic)
                self.entries.extend(page_entries)
                if self.verbose:
                    print(f"[INFO] Scraped page {page}/{page_count}")

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
            self.scrape(topic, max_page_limit, reverse)

        finally:
            self.browser.quit()

    def open_search_page(self) -> None:
        website = SELECTORS["website"]
        wait_for = SELECTORS["search"]["input"]

        self.driver.get(website)
        time.sleep(1)

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, wait_for))
        )

        return

    def submit_search(self, topic: str) -> None:
        input_element_id = SELECTORS["search"]["input"]
        button_element_selector = SELECTORS["search"]["button"]

        search_box = self.driver.find_element("id", input_element_id)
        search_box.clear()
        search_box.send_keys(topic)

        submit_btn = self.driver.find_element(
            "css selector", button_element_selector)
        submit_btn.click()
        time.sleep(2)

        self.topic_url = self.driver.current_url
        return

    def get_total_pages(self) -> int:
        last_page_element_selector = SELECTORS["entry"]["total_page"]
        try:
            last_page_element = self.driver.find_element(
                "css selector", last_page_element_selector)
            return int(last_page_element.text)
        except:
            return 1

    def scroll_to_bottom(self) -> None:
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    def scrape_page(self, page_num: int, topic: str) -> List[TopicBaseResponse]:
        container_class = SELECTORS["entry"]["container"]
        author_class = SELECTORS["entry"]["author"]
        date_class = SELECTORS["entry"]["date"]
        content_class = SELECTORS["entry"]["content"]

        url = self.topic_url if page_num == 1 else f"{self.topic_url}?p={page_num}"
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, container_class))
            )
        except Exception as e:
            print(f"[WARN] No entries found on page {page_num}: {e}")

        self.scroll_to_bottom()

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        results = []

        entry_items = soup.select(container_class)
        for item in entry_items:
            content_div = item.select_one(content_class)
            author_a = item.select_one(author_class)
            date_a = item.select_one(date_class)

            entry = TopicBaseResponse(
                topic=topic,
                content=content_div.get_text(
                    separator=" ", strip=True) if content_div else None,
                author=author_a.text.strip() if author_a else None,
                date=date_a.text.strip() if date_a else None,
            )

            results.append(entry)

        return results

    def restart_driver(self) -> None:
        if self.browser:
            self.browser.quit()

        self.browser = get_browser_driver(
            name=self.driver_name,
            headless=self.headless,
            binary_location=self.binary_location,
            version_main=self.version_main
        )
        self.driver = self.browser.driver
        return
