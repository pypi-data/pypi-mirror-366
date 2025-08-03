from collections.abc import Generator
from ...mcp_manager.client import ClientManagerMCP
from abc import ABC, abstractmethod


class LLM(ABC):
    def __init__(self):
        self.client_manager_mcp: ClientManagerMCP = ClientManagerMCP()
        self.current_language: str = "English"

    @abstractmethod
    def preprocess_query(self, query: str) -> dict:
        """
        Devuelve una lista con todas las querys en las que se divide la query principal y el lenguaje usado en la query. Puede ser solo una query
        """
        pass

    @abstractmethod
    def append_chat_history(self):
        pass

    @abstractmethod
    def simple_query(
        self, query: str, use_services_contex: bool = False
    ) -> Generator[str, None]:
        pass

    @abstractmethod
    def select_prompts(self, query: str) -> str:
        pass

    @abstractmethod
    def select_service(
        self, query: str, extra_messages: list[dict[str, str]] = []
    ) -> str:
        pass

    @abstractmethod
    def final_response(self, query: str, data: str | dict) -> Generator[str, None]:
        pass
