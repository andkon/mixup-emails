# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emoji',
            options={'ordering': ('-created',)},
        ),
        migrations.AddField(
            model_name='emoji',
            name='created',
            field=models.DateTimeField(default=datetime.date(2014, 11, 27), auto_now_add=True),
            preserve_default=False,
        ),
    ]
