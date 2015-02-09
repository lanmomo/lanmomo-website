# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='location',
            new_name='endroit',
        ),
        migrations.RenameField(
            model_name='serveur',
            old_name='modes',
            new_name='mode',
        ),
        migrations.AlterField(
            model_name='serveur',
            name='adresse',
            field=models.CharField(max_length=60),
            preserve_default=True,
        ),
    ]
