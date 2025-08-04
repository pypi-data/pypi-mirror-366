from io import FileIO
from pathlib import Path
from typing import Generator
from uuid import uuid4
import logging

from minio import Minio

from adapter_client.core.domain import model

from ..base import FileStorageInterface


logger = logging.getLogger(__name__)


class S3StorageInterface(FileStorageInterface):
    """Реализация интерфейса к файловому хранилищу S3."""

    _bucket_name = 'attachment'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        storage_config = self._config.file_storage_config

        self._client = Minio(
            endpoint=storage_config['s3_endpoint'],
            access_key=storage_config['s3_access_key'],
            secret_key=storage_config['s3_secret_key'],
            secure=storage_config['s3_use_tls'],
        )

    def store_attachments(self, *files: FileIO) -> Generator[model.Attachment, None, None]:
        logger.info('Сохранение %s исходящих вложений в хранилище адаптера' % len(files))
        for file in files:
            attachment_id = str(uuid4())
            path_in_a_bucket = (Path('tmp') / Path(attachment_id) / Path(file.name).name).as_posix()
            self._client.put_object(
                self._bucket_name,
                path_in_a_bucket,
                data=file,
                length=Path(file.name).stat().st_size,
            )
            yield model.Attachment(
                attachment_id=attachment_id,
                file_path=path_in_a_bucket,
                file_absolute_url=self._client.presigned_get_object(self._bucket_name, path_in_a_bucket)
            )

    def resolve_absolute_urls(
        self, client_id: str, *attachments: model.Attachment
    ) -> Generator[model.Attachment, None, None]:
        logger.info('Получение абсолютных ссылок на %s входящих вложений из хранилища адаптера' % len(attachments))
        for attachment in attachments:
            if attachment.transfer_method == model.AttachmentTransferMethodType.MTOM:
                path_in_a_bucket = (Path('in') / client_id / attachment.file_path).as_posix()
            else:
                path_in_a_bucket = (Path('in') / attachment.attachment_id / client_id / attachment.file_path).as_posix()

            attachment.file_absolute_url = self._client.presigned_get_object(self._bucket_name, path_in_a_bucket)
            yield attachment
