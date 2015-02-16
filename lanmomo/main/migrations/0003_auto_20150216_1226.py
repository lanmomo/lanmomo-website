# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150208_2210'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='participants',
            field=models.ManyToManyField(to='main.Utilisateur'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='utilisateur',
            name='active',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jeu',
            name='description',
            field=models.TextField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serveur',
            name='adresse',
            field=models.CharField(max_length=200),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serveur',
            name='description',
            field=models.TextField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='username',
            field=models.CharField(default=b'anon', max_length=30),
            preserve_default=True,
        ),
    ]
