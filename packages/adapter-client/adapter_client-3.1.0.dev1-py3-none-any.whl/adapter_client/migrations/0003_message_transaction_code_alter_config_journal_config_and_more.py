from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        (
            "adapter_client",
            "0002_alter_journalentry_options_config_adapter_interface_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="transaction_code",
            field=models.CharField(
                blank=True,
                max_length=1500,
                null=True,
                verbose_name="Код транзакции из СМЭВ",
            ),
        ),
    ]
