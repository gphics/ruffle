# Generated by Django 5.1 on 2024-09-07 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='public_id',
            field=models.CharField(default='KgCoF5hqWJipkH88Rxfx4K', max_length=50),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='public_id',
            field=models.CharField(default='KgCoF5hqWJipkH88Rxfx4K', max_length=50),
        ),
    ]
