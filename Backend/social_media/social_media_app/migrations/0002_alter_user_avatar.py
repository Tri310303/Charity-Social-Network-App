# Generated by Django 4.2.6 on 2024-02-23 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(null=True, upload_to='avatars/%Y/%m'),
        ),
    ]
