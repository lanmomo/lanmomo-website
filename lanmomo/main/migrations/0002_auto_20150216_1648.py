# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='event',
        ),
        migrations.AddField(
            model_name='event',
            name='games',
            field=models.ManyToManyField(to='main.Server'),
            preserve_default=True,
        ),
    ]
