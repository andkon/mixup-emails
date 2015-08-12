# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0004_emojiset_emojis'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newsletter',
            name='date',
        ),
        migrations.AddField(
            model_name='newsletter',
            name='send_date',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
