# Generated by Django 5.1 on 2024-08-31 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_profile_public_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], default='Male', max_length=6),
        ),
        migrations.AlterField(
            model_name='profile',
            name='public_id',
            field=models.CharField(default='9GAdjPzCkthYLsF3gj9WMm', max_length=40),
        ),
    ]
