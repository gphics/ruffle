# Generated by Django 5.1 on 2024-09-16 06:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('public_id', models.CharField(default='6xVyi7g3VpmaWNuA35LDsU', max_length=50)),
                ('author', models.CharField(max_length=50)),
                ('content', models.TextField(blank=True, null=True)),
                ('media', models.JSONField()),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report', to='news.post')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
