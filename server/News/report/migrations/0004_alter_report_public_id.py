# Generated by Django 5.1 on 2024-09-21 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0003_alter_report_public_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='public_id',
            field=models.CharField(default='Nzk8d74ZFifGyEzioVuxJm', max_length=50),
        ),
    ]
