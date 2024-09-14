# Generated by Django 5.1 on 2024-09-14 10:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_channel_public_id_alter_publisher_public_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='public_id',
            field=models.CharField(default='3rFXGjFmiGC28UmgG57SNy', max_length=50),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='publishers', to='main.channel'),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='public_id',
            field=models.CharField(default='3rFXGjFmiGC28UmgG57SNy', max_length=50),
        ),
    ]