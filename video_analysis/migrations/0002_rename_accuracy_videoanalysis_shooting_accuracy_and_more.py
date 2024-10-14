# Generated by Django 4.2.16 on 2024-10-11 10:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video_analysis', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='videoanalysis',
            old_name='accuracy',
            new_name='shooting_accuracy',
        ),
        migrations.RenameField(
            model_name='videoanalysis',
            old_name='angle',
            new_name='shooting_angle',
        ),
        migrations.RemoveField(
            model_name='videoanalysis',
            name='compressed_video',
        ),
        migrations.RemoveField(
            model_name='videoanalysis',
            name='processed',
        ),
    ]
