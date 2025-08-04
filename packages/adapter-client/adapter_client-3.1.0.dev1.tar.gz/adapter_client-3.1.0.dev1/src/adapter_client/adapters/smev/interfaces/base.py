# coding: utf-8
from abc import ABC
from abc import abstractmethod
from io import FileIO
from typing import TYPE_CHECKING
from typing import Any
from typing import Generator
from typing import Iterator
from typing import Optional

from adapter_client.core.domain import model


if TYPE_CHECKING:
    from dataclasses import dataclass  # noqa
else:
    from pydantic.dataclasses import dataclass  # noqa


@dataclass
class ExchangeResult:

    """Результат выполнения запроса."""

    request_type: model.RequestType
    message_metadata: Optional[model.MessageMetadataInterface] = None
    request: Any = None
    response: Any = None
    error: Any = None
    result: Any = None
    address: str = None


class AbstractInterface(ABC):

    """Интерфейс к Адаптеру.

    Зона ответственности — непосредственная отправка запросов в Адаптер.
    """

    def __init__(self, config: model.Config):
        assert isinstance(config, model.Config)
        self._config = config

    @abstractmethod
    def send(
        self,
        *outgoing_messages: Iterator[model.OutgoingMessage]
    ) -> Iterator[ExchangeResult]:
        """Отправка пакета сообщений."""

    def find(
        self,
        *outgoing_messages: Iterator[model.OutgoingMessage]
    ) -> Iterator[ExchangeResult]:
        """Получение ответов для пакета сообщений."""

    def get(self) -> ExchangeResult:
        """Получение запроса.

        Получает последний запрос из очереди.
        """

class FileStorageInterface(ABC):
    """Интерфейс к файловому хранилищу.

    Зона ответственности — работа с файлами вложений:
     * Подготовка исходящих вложений к отправке сообщения (загрузка на файловое хранилище адаптера).
     * Подготовка входящих вложений к обработке в РИС (формирование абсолютных ссылок на файл в хранилище).
    """

    def __init__(self, config: model.Config):
        assert isinstance(config, model.Config)
        self._config = config



    @abstractmethod
    def store_attachments(self, *files: FileIO, ) -> Generator[model.Attachment, None, None]:
        """Сохраняет вложения в файловое хранилище."""


    @abstractmethod
    def resolve_absolute_urls(
        self, *attachments: model.Attachment
    ) -> Generator[model.Attachment, None, None]:
        """Подготавливает вложения к обработке в РИС."""
