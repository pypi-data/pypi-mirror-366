# coding: utf-8
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Generator
from typing import Union

from adapter_client.adapters.smev.logging import AbstractJournal  # noqa - обратная совместимость
from adapter_client.core.domain import model


if TYPE_CHECKING:
    from uuid import UUID


class AbstractConfigRepository(ABC):

    @abstractmethod
    def load_config(self) -> model.Config:
        """Загрузить кофигурацию адаптера."""

    @abstractmethod
    def write_config(self, config: model.Config) -> None:
        """Записать кофигурацию адаптера."""


class AbstractOutgoingMessageRepository(ABC):

    """Абстрактное хранилище исходящих сообщений."""

    def __init__(self, config: model.Config) -> None:
        assert isinstance(config, model.Config)
        self._config = config

    @abstractmethod
    def add(self, reply: model.OutgoingMessage) -> model.OutgoingMessage:
        """Добавить исходящее сообщение."""

    @abstractmethod
    def update(self, reply: model.OutgoingMessage) -> model.OutgoingMessage:
        """Обновить исходящее сообщение."""

    @abstractmethod
    def get_pending_messages(self) -> Generator[
        model.OutgoingMessage, None, None
    ]:
        """Получить исходящие сообщения ожидающие отправки."""

    @abstractmethod
    def get_unreplied_messages(self) -> Generator[
        model.OutgoingMessage, None, None
    ]:
        """Получить исходящие сообщения ожидающие ответа."""

    @abstractmethod
    def get_by_client_id(
        self,
        client_id: Union['UUID', str]
    ) -> 'model.OutgoingMessage':
        """Получить исходящее сообщение по client_id сообщения."""


class AbstractIncomingMessageRepository(ABC):

    """Абстрактное хранилище входящих сообщений."""

    def __init__(self, config: model.Config) -> None:
        assert isinstance(config, model.Config)
        self._config = config

    @abstractmethod
    def add(self, reply: model.IncomingMessage) -> model.IncomingMessage:
        """Добавить входящее сообщение."""

    @abstractmethod
    def update(self, reply: model.IncomingMessage) -> model.IncomingMessage:
        """Обновить входящее сообщение."""

    @abstractmethod
    def get_pending_messages(self) -> Generator[
        model.IncomingMessage, None, None
    ]:
        """Получить входящие сообщения ожидающие обработки в РИС."""

    @abstractmethod
    def get_by_client_id(
        self,
        client_id: Union['UUID', str]
    ) -> 'model.IncomingMessage':
        """Получить входящее сообщение по client_id сообщения."""
