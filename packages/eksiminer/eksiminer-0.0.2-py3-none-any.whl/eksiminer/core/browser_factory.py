import time
from typing import Optional
from .base_driver import BaseBrowser
from .drivers.uc_driver import UCDriver


def get_browser_driver(
        name: str = "uc",
        headless: bool = False,
        binary_location: str = None,
        version_main: Optional[int] = None
) -> BaseBrowser:
    time.sleep(1)  # Ensure the environment is ready

    if name == "uc":
        return UCDriver(headless=headless, binary_location=binary_location, version_main=version_main)

    raise NotImplementedError(f"Browser driver '{name}' not implemented")
