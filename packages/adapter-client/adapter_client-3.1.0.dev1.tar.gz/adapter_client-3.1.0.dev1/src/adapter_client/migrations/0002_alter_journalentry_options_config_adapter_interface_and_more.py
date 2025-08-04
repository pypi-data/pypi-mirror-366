from django.db import migrations
from django.db import models
import django.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):

    dependencies = [
        ("adapter_client", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="journalentry",
            options={
                "ordering": ("timestamp",),
                "verbose_name": "Запись журнала обмена",
                "verbose_name_plural": ("Записи журнала обмена",),
            },
        ),
        migrations.AddField(
            model_name="config",
            name="adapter_interface",
            field=models.CharField(
                blank=True,
                default="adapter_client.adapters.smev.interfaces.soap.interface.Interface",
                max_length=200,
                null=True,
                verbose_name="Используемый интерфейс",
            ),
        ),
        migrations.AddField(
            model_name="config",
            name="incoming_message_repository",
            field=models.CharField(
                blank=True,
                default="adapter_client.adapters.db.IncomingMessageRepository",
                max_length=200,
                null=True,
                verbose_name="Репозиторий входящих сообщений",
            ),
        ),
        migrations.AddField(
            model_name="config",
            name="journal",
            field=models.CharField(
                blank=True,
                default="adapter_client.adapters.db.Journal",
                max_length=200,
                null=True,
                verbose_name="Журнал обмена",
            ),
        ),
        migrations.AddField(
            model_name="config",
            name="journal_config",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True, null=True, verbose_name="Конфигурация журнала обмена"
            ),
        ),
        migrations.AddField(
            model_name="config",
            name="outgoing_message_repository",
            field=models.CharField(
                blank=True,
                default="adapter_client.adapters.db.OutgoingMessageRepository",
                max_length=200,
                null=True,
                verbose_name="Репозиторий исходящих сообщений",
            ),
        ),
        migrations.AddField(
            model_name="config",
            name="request_timeout_sec",
            field=models.IntegerField(
                blank=True, default=10, null=True, verbose_name="Таймаут запроса"
            ),
        ),
        migrations.AlterField(
            model_name="config",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="attachments",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True, null=True, verbose_name="Вложения запроса"
            ),
        ),
    ]
