# Generated by Django 5.0.6 on 2024-06-03 23:19

import shortuuid.main
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_alter_group_name_alter_message_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(default=shortuuid.main.ShortUUID.uuid, max_length=200),
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.TextField(),
        ),
    ]
