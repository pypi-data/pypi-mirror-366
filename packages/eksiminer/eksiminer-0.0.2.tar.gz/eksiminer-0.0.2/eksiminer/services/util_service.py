import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .selectors import SELECTORS
from ..core.browser_factory import get_browser_driver
from ..core.schemas import TopicBaseResponse


def get_entry_from_url(
        url: str,
        sync_driver: str = "uc",
        headless: bool = False,
        binary_location: Optional[str] = None,
        version_main: Optional[int] = None
) -> Dict[str, str]:
    """Get entry details from a URL.

    Args:
        url (str): The URL of the entry.
        sync_driver (str, optional): The sync driver to use. Defaults to "uc".
        headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
        binary_location (Optional[str], optional): Path to the browser binary. Defaults to None.
        version_main (Optional[int], optional): Main version of the browser. Defaults to None.

    Raises:
        e: An error occurred while scraping entry from URL.

    Returns:
        Dict[str, str]: A list of dictionaries containing entry details.

        {
            'content': "öcü gibi korkuyorlar senden başkanım! haklılar, korkmalılar! seni başkan yapacağız! unutmayacağız seni, çıkaracağız en kısa zamanda. ama bir söz ver bize, başkan seçilince beştepe'ye geçme. çankaya köşkü yakışır sana.", 
            'author': 'sequasa', 
            'date': '25.03.2025 23:11', 
            'title': 'ekrem imamoğlu'
        }
    """

    content_class = SELECTORS["entry_from_url"]["content"]
    author_class = SELECTORS["entry_from_url"]["author"]
    date_class = SELECTORS["entry_from_url"]["date"]
    title_class = SELECTORS["entry_from_url"]["title"]

    browser = get_browser_driver(
        name=sync_driver, headless=headless, binary_location=binary_location, version_main=version_main
    )
    driver = browser.driver

    try:
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, content_class))
            )
        except Exception as e:
            print(f"[WARN] Entry content did not appear: {e}")

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        content_div = soup.select_one(content_class)
        author_a = soup.select_one(author_class)
        date_a = soup.select_one(date_class)
        title_h1 = soup.select_one(title_class)

        record = TopicBaseResponse(
            topic=title_h1.text.strip() if title_h1 else None,
            content=content_div.get_text(
                separator=" ", strip=True) if content_div else None,
            author=author_a.text.strip() if author_a else None,
            date=date_a.text.strip() if date_a else None
        )

        return record.model_dump()

    except Exception as e:
        print(f"[ERROR] An error occurred while scraping entry from URL: {e}")
        raise e

    finally:
        browser.quit()
