from datetime import datetime
from functools import partial
from typing import Dict
import base64
import json
import logging

from lxml import etree
from opensearch_logger import OpenSearchHandler
from pydantic.json import custom_pydantic_encoder
from zeep.helpers import serialize_object
from zeep.xsd.valueobjects import CompoundValue

from adapter_client.adapters.smev.interfaces.base import ExchangeResult
from adapter_client.adapters.smev.logging import AbstractWriteOnlyJournal
from adapter_client.core.domain import model


LEVEL = logging.INFO


class OpenSearchJournal(AbstractWriteOnlyJournal):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(LEVEL)
        self.logger.propagate = False

        assert self.logger.isEnabledFor(LEVEL)

        class OpenSearchHandler_(OpenSearchHandler):
            def handle(self, record):
                result = super().handle(record)
                self.flush()
                return result

        if not self.logger.hasHandlers():

            journal_config = self._config.journal_config

            self.logger.addHandler(OpenSearchHandler_(
                hosts=[journal_config['opensearch_address']],
                index_name=journal_config['opensearch_index_name'],
                http_auth=(journal_config['opensearch_username'], journal_config['opensearch_password']),
                http_compress=True,
                use_ssl=True,
                verify_certs=False,
                ssl_assert_hostname=False,
                ssl_show_warn=False,
                level=LEVEL,
                raise_on_index_exc=True  # Важно, чтобы не терять логи!
            ))

    def log_exchange_result(self, exchange_result: ExchangeResult) -> model.JournalEntry:
        log = self._get_log_from_result(exchange_result)
        self.logger.log(LEVEL, f'Запрос {datetime.now().astimezone()}', extra=log)
        return self._get_entry_from_result(exchange_result)

    def _get_log_from_result(self, exchange_result: ExchangeResult) -> Dict[str, dict]:
        _json_encoders = {
            CompoundValue: serialize_object,
            etree._Element: partial(etree.tostring, encoding='unicode'),
            # для обратного преобразования байтов PKCS7 подписи в base64
            bytes: lambda o: base64.b64encode(o).decode('ascii'),
            Exception: str,
        }

        json_encoder = partial(custom_pydantic_encoder, _json_encoders)

        log = json.loads(json.dumps(exchange_result, default=json_encoder))

        # Нельзя сохранить список из разных типов: [1, 'Send'], преобразуем в словарь
        log['request_type'] = log.get('request_type') or {}
        if log['request_type']:
            log['request_type'] = {
                'id': log['request_type'][0],
                'name': log['request_type'][1],
            }

        message_metadata = log['message_metadata'] = log.get('message_metadata') or {}
        status = message_metadata.get('status')
        if message_metadata and status:
            message_metadata['status'] = {
                'id': status[0],
                'name': status[1],
            }

        return dict(result=log)

    def _get_entry_from_result(self, exchange_result: ExchangeResult) -> model.JournalEntry:
        message = (
            exchange_result.message_metadata.message
            if exchange_result.message_metadata
            else None
        )
        params = {
            'message': message,
            'request': exchange_result.request,
            'response': exchange_result.response,
            'address': exchange_result.address,
            'type': exchange_result.request_type,
            # на случай, если error является Exception
            'error': str(exchange_result.error)
        }
        return model.JournalEntry(**params)
