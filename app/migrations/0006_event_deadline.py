# Generated by Django 3.1.2 on 2020-11-08 14:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20201108_1359'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='締め切り日時'),
        ),
    ]