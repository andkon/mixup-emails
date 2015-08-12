# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0007_auto_20141210_2229'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsletter',
            name='send_task',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
    ]
