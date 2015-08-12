# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0008_newsletter_send_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlistclick',
            name='clicked_on',
            field=models.DateTimeField(default=datetime.date(2014, 12, 18), auto_now_add=True),
            preserve_default=False,
        ),
    ]
