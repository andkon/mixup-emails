# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0005_auto_20141209_1817'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailprofile',
            name='invited_by',
            field=models.ForeignKey(blank=True, to='emails.EmailProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailprofile',
            name='is_confirmed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailprofile',
            name='is_subscribed',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailprofile',
            name='joined',
            field=models.DateTimeField(default=datetime.date(2014, 12, 10), auto_now_add=True),
            preserve_default=False,
        ),
    ]
