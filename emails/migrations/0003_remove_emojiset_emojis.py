# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0002_auto_20141127_1650'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emojiset',
            name='emojis',
        ),
    ]
