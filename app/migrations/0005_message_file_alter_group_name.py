# Generated by Django 5.0.6 on 2024-05-30 02:53

import shortuuid.main
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0004_group_is_private_group_users_alter_group_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="file",
            field=models.FileField(blank=True, null=True, upload_to="files/"),
        ),
        migrations.AlterField(
            model_name="group",
            name="name",
            field=models.CharField(
                default=shortuuid.main.ShortUUID.uuid, max_length=200
            ),
        ),
    ]
