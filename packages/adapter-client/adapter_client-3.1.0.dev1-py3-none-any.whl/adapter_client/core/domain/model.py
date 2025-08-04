# coding: utf-8
from abc import ABC
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from uuid import uuid4

from pydantic.fields import Field


if TYPE_CHECKING:
    from dataclasses import dataclass  # noqa
else:
    from pydantic.dataclasses import dataclass  # noqa


class ConfigNotValid(Exception):

    def __init__(self, description: str, config: 'Config', *args):
        assert isinstance(config, Config)
        self.config = config

        message = (
            'Клиент адаптера СМЭВ настроен неверно:\n\n'
            f'{description}'
        )

        super().__init__(message, *args)


@dataclass
class Config:

    # Настройки РИС
    adapter_address: Optional[str] = Field(
        title='Адрес web-сервиса Адаптера',
        default=None
    )
    app_mnemonics: Optional[str] = Field(
        title='Наименование мнемоники информационной системы',
        default=None
    )
    node_mnemonics: Optional[str] = Field(
        title='Мнемоника узла информационной системы',
        default=None
    )

    # Настройки отправки сообщения
    send_request_retry_time: int = Field(
        title='Период переотправки запроса SendRequest',
        default=10
    )
    send_request_retry_count: int = Field(
        title=(
            'Количество попыток отправки SendRequest в случае ошибки Адаптера'
        ),
        default=3,
    )

    get_request_retry_time: int = Field(
        title='Периодичность отправки запроса GetRequest',
        default=3,
    )

    # Настройки поиска сообщения
    find_request_retry_time: int = Field(
        title='Период опроса Адаптера на наличие ответов СМЭВ',
        default=30
    )

    # Настройки интерфейсов
    request_timeout_sec: int = Field(
        title='Таймаут запроса',
        default=10
    )

    # Используемые компоненты адаптера
    adapter_interface: str = Field(
        title='Используемый интерфейс',
        default=(
            'adapter_client.adapters.smev.interfaces.soap.interface.Interface'
        )
    )
    outgoing_message_repository: str = Field(
        title='Репозиторий исходящих сообщений',
        default='adapter_client.adapters.db.OutgoingMessageRepository'
    )
    incoming_message_repository: str = Field(
        title='Репозиторий входящих сообщений',
        default='adapter_client.adapters.db.IncomingMessageRepository'
    )
    journal: str = Field(
        title='Журнал обмена',
        default='adapter_client.adapters.db.Journal'
    )
    journal_config: Optional[Dict] = Field(
        title='Конфигурация журнала обмена',
        default=None
    )
    file_storage_interface: Optional[str] = Field(
        title=' Интерфейс к файловому хранилищу',
        default='adapter_client.adapters.smev.interfaces.s3_storage.interface.S3StorageInterface'
    )
    file_storage_config: Optional[Dict] = Field(
        title='Конфигурация интерфейса к файловому хранилищу',
        default=None
    )

    id: int = 1

    def validate(self):
        errors = []

        for field_name in (
            'adapter_address',
            'app_mnemonics'
        ):
            if not getattr(self, field_name):
                errors.append(
                    'Не заполнено поле '
                    f'"{getattr(type(self), field_name).title}"'
                )

        if (
            self.journal == 'adapter_client.adapters.smev.logging.opensearch.OpenSearchJournal' and
            not all((
                self.journal_config.get('opensearch_address'), self.journal_config.get('opensearch_index_name'),
                self.journal_config.get('opensearch_username'), self.journal_config.get('opensearch_password')
            ))
        ):
            errors.append('Не произведена настройка OpenSearch')

        if (
            self.file_storage_interface == 'adapter_client.adapters.smev.interfaces.s3_storage.interface.S3StorageInterface' and
            (
                not self.file_storage_config or
                not all(i is not None for i in (
                    self.file_storage_config.get('s3_endpoint'), self.file_storage_config.get('s3_access_key'),
                    self.file_storage_config.get('s3_secret_key'), self.file_storage_config.get('s3_use_tls')
                ))
            )
        ):
            errors.append('Не произведена настройка файлового хранилища (s3)')

        if errors:
            raise ConfigNotValid('\n'.join(errors), self)


class NamedIntEnum(Enum):
    def __init__(self, id_: int, verbose: str) -> None:
        self.id = id_
        self.verbose = verbose


class OutgoingStatus(NamedIntEnum):

    new = (1, 'Новый')
    sent = (2, 'Отправлен в Адаптер')
    retry = (3, 'Повторная отправка')
    error = (4, 'Ошибка отправки')


class IncomingStatus(NamedIntEnum):
    received = (1, 'Получен')
    error = (2, 'Ошибка ответа')
    processed = (3, 'Обработано РИС')


class RequestType(NamedIntEnum):
    send = (1, 'Send')
    get = (2, 'Get')
    find = (3, 'Find')

class AttachmentTransferMethodType(NamedIntEnum):
    MTOM = (1, 'В составе сообщения')
    REFERENCE = (2, 'Отдельно от сообщения')


@dataclass
class Attachment:
    """Объект содержащий информацию о вложениях в/из РИС.


    Attachment(
        attachment_id='e84029b8-2efc-11ef-9e0f-360b245a0e4a',
        file_path='f4_ProfessionalActivitiesFirst.FileUploadComponent.ProfessionalActivitiesFirst.3501262014',
        file_absolute_url=(
            'http://192.168.231.65/attachment/in/'
            'e84029b8-2efc-11ef-9e0f-360b245a0e4a/e83e7c07-2efc-11ef-9e0f-360b245a0e4a/'
            'f4_ProfessionalActivitiesFirst.FileUploadComponent.ProfessionalActivitiesFirst.3501262014'
        ),
        transfer_method=AttachmentTransferMethodType.REFERENCE
    )
    """

    attachment_id: Union[str, None] = Field(
        title='Идентификатор вложения',
        description='Обязательно заполняется, если transfer_method==AttachmentTransferMethodType.REFERENCE',
        default=None,
    )
    file_path: str = Field(
        title='Полный (абсолютный) либо относительный путь к файлу вложения',
        description='В случае отправки исходящего вложения указывается полный путь в хранилище',
    )
    file_absolute_url: Union[str, None] = Field(
        title='Абсолютный URL до файла в хранилище',
        description='Обязателен для обработки в РИС',
        default=None
    )
    transfer_method: AttachmentTransferMethodType = AttachmentTransferMethodType.REFERENCE


@dataclass
class Message:

    """Объект содержащий сообщение в/из РИС.

    РИС отправляет и получает на обработку объекты этого типа.
    """

    message_type: str = Field(
        title='Вид сведений',
    )

    body: str = Field(
        title='Тело запроса'
    )
    attachments: List[Attachment] = Field(
        title='Вложения запроса',
        default_factory=list,
    )
    client_id: str = Field(
        title='Клиентский идентификатор запроса',
        default_factory=lambda: str(uuid4()),
    )
    message_id: Union[str, None] = Field(
        title='Идентификатор запроса СМЭВ 3',
        default=None,
    )
    transaction_code: Union[str, None] = Field(
        title='Код транзакции из СМЭВ',
        default=None,
        max_length=1500
    )
    reference_message_id: Optional[str] = Field(
        title='Идентификатор корневого запроса '
              '(запроса, порождающего цепочку запросов)',
        default=None,
    )
    reply_to: Optional['Message'] = Field(
        title='Сообщение, на которое пришел ответ',
        default=None,
    )

    test: bool = Field(
        title='Признак тестового взаимодействия',
        default=False,
    )
    id: Union[int, None] = Field(
        title='Идентификатор сообщения',
        default=None,
    )


@dataclass
class MessageMetadataInterface(ABC):
    """Общие поля метаданных сообщения."""
    id: Union[int, None] = Field(
        title='Идентификатор служебных данных сообщения',
        default=None,
    )
    message: Message = Field(
        title='Сообщение'
    )
    status: NamedIntEnum = Field(
        title='Статус сообщения',
    )
    timestamp: datetime = Field(
        title='Дата и время создания',
        default_factory=lambda: datetime.now().astimezone()
    )


@dataclass
class OutgoingMessage(MessageMetadataInterface):

    """Объект со служебной информацией об исходящем сообщении.

    Используются адаптером и не содержат полезной для РИС информации.
    """

    id: Union[int, None] = Field(
        title='Идентификатор исходящего сообщения',
        default=None,
    )
    status: OutgoingStatus = Field(
        title='Статус исходящего сообщения',
        default=OutgoingStatus.new
    )
    attempts: int = Field(
        title='Количество попыток отправки',
        default=0
    )


@dataclass
class IncomingMessage(MessageMetadataInterface):

    """Объект со служебной информацией о входящем сообщении.

    Используются адаптером и не содержат полезной для РИС информации.
    """
    id: Union[int, None] = Field(
        title='Идентификатор входящего сообщения',
        default=None,
    )
    status: IncomingStatus = Field(
        title='Статус входящего сообщения',
        default=IncomingStatus.received
    )


@dataclass
class JournalEntry:
    address: str = Field(
        title='Адрес запроса',
        default=None,
    )
    timestamp: datetime = Field(
        title='Дата отправки',
        default_factory=lambda: datetime.now().astimezone()
    )
    type: RequestType = Field(
        title='Тип запроса'
    )
    request: str = Field(
        title='Запрос',
        default=None,
    )
    response: str = Field(
        title='Ответ',
        default=None,
    )
    error: str = Field(
        title='Ошибка',
        default=None,
    )
    message: Message = Field(
        title='Сообщение',
        default=None,
    )
    id: Optional[str] = Field(
        title='Идентификатор записи журнала',
        default=None
    )
