# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-08-16 00:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kiosk', '0003_auto_20170815_2358'),
    ]

    operations = [
        migrations.RenameField(
            model_name='office',
            old_name='zip',
            new_name='zip_code',
        ),
    ]
