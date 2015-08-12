# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0003_remove_emojiset_emojis'),
    ]

    operations = [
        migrations.AddField(
            model_name='emojiset',
            name='emojis',
            field=models.ManyToManyField(related_name=b'in_sets', through='emails.SettedEmoji', to='emails.Emoji'),
            preserve_default=True,
        ),
    ]
