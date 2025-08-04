from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import Generator
from typing import Iterable
from typing import Optional
from typing import Union

from adapter_client.adapters.smev.interfaces.base import ExchangeResult
from adapter_client.core.domain import model


class AbstractWriteOnlyJournal(ABC):

    def __init__(self, config: model.Config) -> None:
        assert isinstance(config, model.Config)
        # Неплохо бы вызвать config.validate() перед присвоением
        # Но сейчас это ломает тесты
        self._config = config

    @abstractmethod
    def log_exchange_result(
        self,
        exchange_result: ExchangeResult
    ) -> model.JournalEntry:
        """Записывает результат обмена в журнал и возвращает запись журнала."""


class AbstractJournal(AbstractWriteOnlyJournal):

    """Абстрактный журнал обмена сообщениями."""

    @abstractmethod
    def get_entries(
        self,
        offset: int = 0,
        limit: int = 25,
        sort_fields: Optional[Iterable[str]] = None,
        client_id: Optional[str] = None,
        request_types: Optional[Iterable[model.RequestType]] = None,
        timestamp_from: Optional[datetime] = None,
        timestamp_to: Optional[datetime] = None,
    ) -> Generator[model.JournalEntry, None, None]:
        """Возвращает генератор с записями журнала."""

    @abstractmethod
    def get_entry_by_id(self, _id: Union[str, int]) -> model.JournalEntry:
        """Возвращает одну запись по id."""
