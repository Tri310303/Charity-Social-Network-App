# Generated by Django 4.2.6 on 2024-02-24 08:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_media_app', '0006_alter_comment_post'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tag',
            new_name='Hashtag',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='tags',
            new_name='hashtag',
        ),
    ]
