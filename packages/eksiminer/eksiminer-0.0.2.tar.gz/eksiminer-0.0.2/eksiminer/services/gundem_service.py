from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .selectors import SELECTORS
from ..core.browser_factory import get_browser_driver
from ..core.schemas import GundemResponse


def _parse_gundem(html: str, selector: str) -> List[GundemResponse]:
    website = SELECTORS["website"]

    soup = BeautifulSoup(html, "html.parser")
    links = soup.select(selector)

    results = []
    for a_tag in links:
        href = a_tag["href"]
        title = a_tag.get_text(strip=False)
        title_list = title.split(" ")
        if title_list[-1].isdigit():
            title = " ".join(title_list[:-1])
            count = title_list[-1]
        else:
            count = "0"
            title = " ".join(title_list)
        full_url = f"{website}{href}"
        results.append(GundemResponse(title=title, url=full_url, count=count))

    return results


def get_gundem(
        headline: Optional[str] = None,
        sync_driver: str = "uc",
        headless: bool = False,
        selector_override: Optional[str] = None,
        binary_location: Optional[str] = None,
        version_main: Optional[int] = None
) -> List[Dict[str, str]]:
    """
    Get the current trending topics from the website.

    Args:
        headline (Optional[str], optional): The headline to filter topics. Defaults to None. 'siyaset' for politics, etc.
        sync_driver (str, optional): The synchronous browser driver to use. Defaults to "uc".
        headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
        selector_override (Optional[str], optional): The CSS selector to use for overriding the default. Defaults to None.
        binary_location (Optional[str], optional): The path to the browser binary. Defaults to None.
        version_main (Optional[int], optional): The main version of the browser to use. Defaults to None.

    Returns:
        List[Dict[str, str]]: The list of trending topics. 
        Example:
        [
            {
                'title': '29 temmuz 2025 özgür özel komisyon açıklaması',
                'url': 'https://eksisozluk.com/29-temmuz-2025-ozgur-ozel-komisyon-aciklamasi--8009885?a=popular',
                'count': '270'
            },
            ...
        ]
    """

    selector = selector_override or SELECTORS["gundem"]["container"]
    wait_for_class = SELECTORS["gundem"]["wait_for_class"]
    website = SELECTORS["website"]

    if headline:
        website = f"{website}/basliklar/kanal/{headline}"

    try:
        browser = get_browser_driver(
            name=sync_driver, headless=headless, binary_location=binary_location, version_main=version_main
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize browser driver: {e}")

    try:
        html = browser.get_html(website, wait_for_class=wait_for_class)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        browser.quit()

    results = _parse_gundem(html, selector)
    results = [result.model_dump() for result in results]
    return results


async def get_gundem_async(
        headline: Optional[str] = None,
        async_driver: str = "uc",
        headless: bool = False,
        selector_override: Optional[str] = None,
        binary_location: Optional[str] = None,
        version_main: Optional[int] = None
) -> List[Dict[str, str]]:

    selector = selector_override or SELECTORS["gundem"]["container"]
    wait_for_class = SELECTORS["gundem"]["wait_for_class"]
    website = SELECTORS["website"]

    if headline:
        website = f"{website}/basliklar/kanal/{headline}"

    try:
        browser = get_browser_driver(
            name=async_driver, headless=headless, binary_location=binary_location, version_main=version_main
        )
        html = await browser.get_html_async(website, wait_for_class=wait_for_class)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        browser.quit()

    results = _parse_gundem(html, selector)
    return results
