# Generated by Django 2.2.6 on 2020-11-18 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20201118_1347'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='active',
        ),
    ]
