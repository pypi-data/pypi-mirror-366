from abc import ABC, abstractmethod


class BaseBrowser(ABC):

    @abstractmethod
    def get_html(self, url: str, wait_for_class: str = None, timeout: int = 10) -> str:
        pass

    @abstractmethod
    async def get_html_async(self, url: str, wait_for_class: str = None, timeout: int = 10) -> str:
        pass

    @abstractmethod
    def quit(self) -> None:
        pass
