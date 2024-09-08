# Generated by Django 5.1 on 2024-09-07 16:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('public_id', models.CharField(default='67Kyg6YZJhbja3EZzv5MDe', max_length=50)),
                ('name', models.CharField(max_length=100)),
                ('owner', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('avatar_public_id', models.CharField(max_length=50)),
                ('follows', models.JSONField()),
            ],
            options={
                'db_table': 'channel',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('public_id', models.CharField(default='67Kyg6YZJhbja3EZzv5MDe', max_length=50)),
                ('user', models.CharField(max_length=50)),
                ('is_admin', models.BooleanField(default=False)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.channel')),
            ],
            options={
                'db_table': 'publisher',
                'ordering': ['-created_at'],
            },
        ),
    ]