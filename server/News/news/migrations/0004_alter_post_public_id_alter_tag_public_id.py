# Generated by Django 5.1 on 2024-09-21 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_remove_post_likes_alter_post_public_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='public_id',
            field=models.CharField(default='Nzk8d74ZFifGyEzioVuxJm', max_length=50),
        ),
        migrations.AlterField(
            model_name='tag',
            name='public_id',
            field=models.CharField(default='Nzk8d74ZFifGyEzioVuxJm', max_length=50),
        ),
    ]
