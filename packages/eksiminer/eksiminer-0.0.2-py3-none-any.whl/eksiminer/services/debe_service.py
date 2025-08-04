import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Dict, Optional
from .selectors import SELECTORS
from ..core.browser_factory import get_browser_driver
from ..core.schemas import DebeResponse


def get_debe_list(
        sync_driver: str = "uc",
        headless: bool = False,
        binary_location: Optional[str] = None,
        version_main: Optional[int] = None
) -> List[Dict[str, str]]:
    """Get a list of debe entries.

    Args:
        sync_driver (str, optional): Sync driver to use. Defaults to "uc".
        headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
        binary_location (Optional[str], optional): Path to the browser binary. Defaults to None.
        version_main (Optional[int], optional): Main version of the browser. Defaults to None.

    Returns:
        List[Dict[str, str]]: A list of debe entries.

        [
            {
                'title': "esenyurt'ta yayaları durdurup haraç kesen çete",
                'url': 'https://eksisozluk.com/entry/177149240?debe=true'
            },
            ...
        ]
    """
    wait_for_class = SELECTORS["debe"]["wait_for_class"]
    container_class = SELECTORS["debe"]["container"]
    debe_website = SELECTORS["debe_website"]

    browser = get_browser_driver(
        name=sync_driver, headless=headless, binary_location=binary_location, version_main=version_main
    )
    driver = browser.driver

    try:
        driver.get(debe_website)
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, wait_for_class))
            )
        except Exception as e:
            print(f"[WARN] Topic list did not appear: {e}")

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        a_tags = soup.select(container_class)

        results = []
        for a_tag in a_tags:
            href = a_tag.get("href")
            title = a_tag.get_text(strip=True)
            full_url = f"https://eksisozluk.com{href}"
            results.append(DebeResponse(title=title, url=full_url))

        results = [entry.model_dump() for entry in results]
        return results
    except Exception as e:
        print(f"[ERROR] An error occurred while scraping debe list: {e}")
        raise e

    finally:
        browser.quit()
