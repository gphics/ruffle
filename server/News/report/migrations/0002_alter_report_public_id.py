# Generated by Django 5.1 on 2024-09-18 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='public_id',
            field=models.CharField(default='LmDsiD5VtvuTcfFewEMq3Y', max_length=50),
        ),
    ]
