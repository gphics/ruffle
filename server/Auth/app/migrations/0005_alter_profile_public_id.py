# Generated by Django 5.1 on 2024-09-14 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_profile_public_id_alter_profile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='public_id',
            field=models.CharField(default='Lu3AvsoyD7aXB7wuG7ePKZ', max_length=40),
        ),
    ]
